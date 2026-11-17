import os
import streamlit as st
from dotenv import load_dotenv
from transcript_fetcher import TranscriptFetcher
from database import SummaryDatabase
from ai_summarizer import AISummarizer, TemporaryGeminiError
from content_templates import CATEGORY_LABELS

load_dotenv()
st.set_page_config(page_title='YouTube Knowledge Extractor',page_icon='🎓',layout='wide')
@st.cache_resource
def get_db(): return SummaryDatabase(os.getenv('DATABASE_PATH','youtube_knowledge.db'))

def render_content(category,data):
    fields={
    'education':[('🎯 Learning objectives','learning_objectives'),('📚 Topic-wise notes','topic_wise_notes'),('📖 Key definitions','key_definitions'),('🔎 Examples and applications','examples_and_applications'),('⚡ Revision points','revision_points'),('✍️ Practice questions','practice_questions')],
    'entertainment':[('🎬 Storyline','storyline'),('👥 Characters and roles','characters_and_roles'),('❤️ Relationships and conflicts','relationships_and_conflicts'),('🎞️ Important scenes in order','important_scenes_in_order'),('😮 Twists and revelations','twists_and_revelations'),('💬 Emotional moments','emotional_moments'),('🔚 Ending and unresolved questions','ending_and_unresolved_questions')],
    'technical_tutorial':[('🧰 Skills and tools','skills_and_tools'),('📋 Prerequisites','prerequisites'),('🪜 Step-by-step instructions','step_by_step_instructions'),('💻 Code and commands','code_or_commands_mentioned'),('⚠️ Mistakes and tips','common_mistakes_and_tips'),('🧪 Practical exercises','practical_exercises')],
    'podcast_interview':[('🎙️ Speakers','speakers_and_roles'),('🗣️ Discussion','discussion_overview'),('📌 Main topics','main_topics'),('⚖️ Viewpoints','viewpoints_and_arguments'),('💡 Insights','memorable_insights'),('➡️ Conclusions','conclusions_and_follow_up_questions')],
    'news_current_affairs':[('📰 Event summary','event_summary'),('🏛️ People and organizations','people_and_organizations'),('🕒 Timeline','timeline_and_developments'),('🔍 Context','stated_causes_and_context'),('📊 Impacts','impacts_and_consequences'),('❔ Claims to verify','claims_needing_verification')],
    'documentary':[('🌍 Subject','subject_and_scope'),('🧭 Themes','central_themes'),('📅 Chronology','chronology_or_structure'),('🧾 Evidence presented','evidence_and_examples_presented'),('👤 People and places','people_and_places'),('🏁 Findings','findings_and_conclusions')],
    'general':[('Overview','overview'),('Main points','main_points'),('Notable details','notable_details'),('Conclusion','conclusion'),('Follow-up questions','follow_up_questions')]}
    for heading,key in fields.get(category,fields['general']):
        value=data.get(key)
        if value:
            st.markdown('#### '+heading)
            if isinstance(value,list):
                for x in value: st.markdown('- '+x)
            else: st.write(value)


def generate(pending, db):
    if not os.getenv("GEMINI_API_KEY"):
        st.error("Add GEMINI_API_KEY to .env and restart Streamlit.")
        return

    status = st.empty()

    try:
        ai = AISummarizer()

        with st.spinner("AI is processing your video and creating tailored notes..."):

            # Reuse the category if classification already succeeded.
            if pending.get("category"):
                category = pending["category"]
                reason = pending.get("reason", "")

                status.success(
                    f"Using previously detected category: "
                    f"{CATEGORY_LABELS.get(category, 'General')}"
                )

            else:
                cls = ai.classify(
                    pending["text"],
                    lambda message: status.info(message)
                )

                category = cls.category
                reason = cls.reason

                # Save classification immediately so Retry can reuse it.
                pending["category"] = category
                pending["reason"] = reason
                st.session_state["pending_transcript"] = pending

                status.success(
                    f"Detected: {CATEGORY_LABELS[category]} "
                    f"({cls.confidence:.0%} confidence)"
                )

            # Generate content using the detected category.
            notes = ai.generate_category_content(
                pending["text"],
                category,
                lambda message: status.info(message)
            )

        # Save notes and category together.
        db.save_summary(
            pending["video_id"],
            pending["title"],
            notes.model_dump(),
            category
        )

        st.session_state["last_result"] = {
            "video_id": pending["video_id"],
            "title": pending["title"],
            "category": category,
            "reason": reason,
            "content": notes.model_dump()
        }

        st.session_state.pop("pending_transcript", None)

        status.success("Tailored content generated successfully!")
        st.success("Your video notes have been saved to the library.")

    except TemporaryGeminiError as e:
        st.session_state["pending_transcript"] = pending
        st.warning(str(e))
        st.info(
            "Your transcript and any successful classification are cached. "
            "Retry without downloading captions or classifying again."
        )

    except Exception as e:
        st.session_state["pending_transcript"] = pending
        st.error(f"An error occurred: {e}")


db=get_db(); fetcher=TranscriptFetcher()
st.title('🎓 YouTube Knowledge Extractor')
st.write('Understand videos and generate content tailored to what they contain.')
t1,t2=st.tabs(['✨ Extract knowledge','📚 Your library'])
with t1:
    with st.form('extract'):
        url=st.text_input('YouTube video URL',placeholder='https://youtu.be/...')
        title=st.text_input('Video title (optional)')
        language=st.selectbox('Transcript language',['en','hi','es','fr','de'])
        st.caption('Content type: Automatic detection — AI selects the most suitable format.')
        go=st.form_submit_button('Analyze video',type='primary',use_container_width=True)
    if go:
        try:
            vid=fetcher.extract_video_id(url); old=db.get_summary(vid)
            if old:
                st.session_state['last_result']={'video_id':vid,'title':old['title'],'category':old.get('category','general'),'content':old['summary'],'cached':True}
            else:
                cached=db.get_transcript(vid)
                if cached: text=cached['transcript_text'];st.success('Transcript loaded from SQLite cache.')
                else:
                    with st.spinner('Downloading YouTube captions...'): tr=fetcher.fetch(vid,[language])
                    text=tr.text;db.save_transcript(vid,tr.text,tr.language,tr.is_generated);st.success('Transcript fetched · '+tr.language)
                pending={'video_id':vid,'title':title.strip() or 'YouTube video '+vid,'text':text}
                st.session_state['pending_transcript']=pending
                with st.expander('Preview transcript'):st.write(text[:5000]+('…' if len(text)>5000 else ''))
                generate(pending,db)
        except Exception as e:st.error(str(e))
    pending=st.session_state.get('pending_transcript')
    if pending and st.button('🔄 Retry AI Generation',type='primary',use_container_width=True):generate(pending,db)
    result=st.session_state.get('last_result')
    if result:
        st.divider();st.subheader(result['title']);cat=result.get('category','general')
        st.success('Detected content type: '+CATEGORY_LABELS.get(cat,'General'))
        if result.get('reason'):st.caption('Why: '+result['reason'])
        render_content(cat,result['content'])
with t2:
    st.subheader('Previously analyzed videos');q=st.text_input('Search saved notes');items=db.search_summaries(q)
    if not items:st.info('Your library is empty. Analyze a video to save notes.')
    for item in items:
        cat=item.get('category','general')
        with st.expander(f"{item['title']} · {CATEGORY_LABELS.get(cat,'General')} · {item['created_at']}"):
            st.caption('Video ID: '+item['video_id']);render_content(cat,item['summary'])
st.divider();st.caption('Transcripts and category-specific results are stored in SQLite. API key stays in .env.')




