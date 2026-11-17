from typing import Literal
from pydantic import BaseModel, Field

Category = Literal['education','entertainment','technical_tutorial','podcast_interview','news_current_affairs','documentary','general']

class VideoClassification(BaseModel):
    category: Category
    confidence: float = Field(ge=0, le=1)
    reason: str

class EducationContent(BaseModel):
    content_type: Literal['education'] = 'education'
    learning_objectives: list[str]
    topic_wise_notes: list[str]
    key_definitions: list[str]
    examples_and_applications: list[str]
    revision_points: list[str]
    practice_questions: list[str]

class EntertainmentContent(BaseModel):
    content_type: Literal['entertainment'] = 'entertainment'
    storyline: str
    characters_and_roles: list[str]
    relationships_and_conflicts: list[str]
    important_scenes_in_order: list[str]
    twists_and_revelations: list[str]
    emotional_moments: list[str]
    ending_and_unresolved_questions: list[str]

class TechnicalTutorialContent(BaseModel):
    content_type: Literal['technical_tutorial'] = 'technical_tutorial'
    skills_and_tools: list[str]
    prerequisites: list[str]
    step_by_step_instructions: list[str]
    code_or_commands_mentioned: list[str]
    common_mistakes_and_tips: list[str]
    practical_exercises: list[str]

class PodcastInterviewContent(BaseModel):
    content_type: Literal['podcast_interview'] = 'podcast_interview'
    speakers_and_roles: list[str]
    discussion_overview: str
    main_topics: list[str]
    viewpoints_and_arguments: list[str]
    memorable_insights: list[str]
    conclusions_and_follow_up_questions: list[str]

class NewsContent(BaseModel):
    content_type: Literal['news_current_affairs'] = 'news_current_affairs'
    event_summary: str
    people_and_organizations: list[str]
    timeline_and_developments: list[str]
    stated_causes_and_context: list[str]
    impacts_and_consequences: list[str]
    claims_needing_verification: list[str]

class DocumentaryContent(BaseModel):
    content_type: Literal['documentary'] = 'documentary'
    subject_and_scope: str
    central_themes: list[str]
    chronology_or_structure: list[str]
    evidence_and_examples_presented: list[str]
    people_and_places: list[str]
    findings_and_conclusions: list[str]

class GeneralContent(BaseModel):
    content_type: Literal['general'] = 'general'
    overview: str
    main_points: list[str]
    notable_details: list[str]
    conclusion: str
    follow_up_questions: list[str]

CONTENT_MODELS = {
    'education': EducationContent, 'entertainment': EntertainmentContent,
    'technical_tutorial': TechnicalTutorialContent, 'podcast_interview': PodcastInterviewContent,
    'news_current_affairs': NewsContent, 'documentary': DocumentaryContent, 'general': GeneralContent,
}
CATEGORY_LABELS = {
    'education':'Educational / Learning', 'entertainment':'Movies / Dramas / Web Series',
    'technical_tutorial':'Technical Tutorial', 'podcast_interview':'Podcast / Interview',
    'news_current_affairs':'News / Current Affairs', 'documentary':'Documentary', 'general':'General',
}
PROMPTS = {
'education': 'Create topic-wise learning notes, objectives, definitions, transcript-supported examples, revision points and practice questions.',
'entertainment': 'Treat this as a movie, drama or series. Give a coherent storyline, characters and roles, relationships, important scenes in order, twists, emotional moments and ending. Full spoilers are allowed. Never invent scenes or relationships.',
'technical_tutorial': 'Create a practical guide with tools, prerequisites, ordered steps, code or commands actually mentioned, tips and exercises. Never fabricate code.',
'podcast_interview': 'Identify speakers when clear; capture discussion, topics, viewpoints, insights and conclusions. Attribute opinions only when clear.',
'news_current_affairs': 'Summarize reported events, people, timeline, stated context and impacts. Separate reported claims from verified facts; flag claims needing verification.',
'documentary': 'Explain subject, themes, chronology, evidence presented, people and places, findings and conclusions. Do not add outside facts.',
'general': 'Provide an overview, main points, notable details, conclusion and useful follow-up questions.'}
