from pydantic import BaseModel, Field
from typing import Literal


class QuizQuestion(BaseModel):
    question_id: int = Field(
        description="Unique identifier of the question."
    )

    question: str = Field(
        description="The question presented to the student."
    )

    question_type: Literal[
        "multiple_choice",
        "true_false",
        "short_answer"
    ] = Field(
        description="Type of the question."
    )

    choices: list[str] = Field(
        default_factory=list,
        description="Possible answers for multiple-choice questions. Empty for other question types."
    )

    correct_answer: str | bool = Field(
    description="Correct answer. For true/false questions, use a boolean. For multiple-choice and short-answer questions, use a string."
)

    explanation: str = Field(
        description="Explanation of why the answer is correct."
    )

    topic: str = Field(
        description="Specific topic tested by this question."
)


class Quiz(BaseModel):
    title: str = Field(
        description="Title of the quiz."
    )

    topic: str = Field(
        description="Main topic covered by the quiz."
    )

    questions: list[QuizQuestion] = Field(
        description="List of quiz questions."
    )


class StudentAnswer(BaseModel):
    question_id: int = Field(
        description="Identifier of the quiz question."
    )

    answer: str = Field(
        description="Answer provided by the student."
    )


class QuestionEvaluation(BaseModel):
    question_id: int = Field(
        description="Identifier of the evaluated question."
    )

    student_answer: str = Field(
        description="Answer provided by the student."
    )

    correct_answer: str = Field(
        description="Correct answer according to the quiz."
    )

    is_correct: bool = Field(
        description="Whether the student's answer is correct."
    )

    score: float = Field(
        ge=0,
        le=1,
        description="Score obtained for this question, between 0 and 1."
    )

    feedback: str = Field(
        description="Short pedagogical feedback for the student."
    )

    topic: str = Field(
        description="Topic associated with this question."
    )


class QuizEvaluation(BaseModel):
    quiz_title: str = Field(
        description="Title of the evaluated quiz."
    )

    total_questions: int = Field(
        description="Total number of questions."
    )

    correct_answers: int = Field(
        description="Number of correctly answered questions."
    )

    score: float = Field(
        ge=0,
        description="Total score obtained."
    )

    percentage: float = Field(
        ge=0,
        le=100,
        description="Percentage score."
    )

    strong_topics: list[str] = Field(
        default_factory=list,
        description="Topics that the student appears to understand well."
    )

    weak_topics: list[str] = Field(
        default_factory=list,
        description="Topics that require further study."
    )

    question_results: list[QuestionEvaluation] = Field(
        description="Detailed evaluation of every question."
    )

    overall_feedback: str = Field(
        description="Overall pedagogical feedback for the student."
    )


class QuizPerformance(BaseModel):
    quiz_title: str = Field(
        description="Title of the completed quiz."
    )

    score: float = Field(
        ge=0,
        description="Score obtained in the quiz."
    )

    percentage: float = Field(
        ge=0,
        le=100,
        description="Percentage obtained in the quiz."
    )

    weak_topics: list[str] = Field(
        default_factory=list,
        description="Topics that need improvement."
    )

    strong_topics: list[str] = Field(
        default_factory=list,
        description="Topics that are well understood."
    )


class StudentProfile(BaseModel):
    student_id: str = Field(
        description="Unique identifier of the student."
    )

    quizzes_completed: int = Field(
        default=0,
        ge=0,
        description="Number of completed quizzes."
    )

    average_score: float = Field(
        default=0.0,
        ge=0,
        description="Average score across completed quizzes."
    )

    average_percentage: float = Field(
        default=0.0,
        ge=0,
        le=100,
        description="Average percentage across completed quizzes."
    )

    strong_topics: list[str] = Field(
        default_factory=list,
        description="Topics the student generally understands well."
    )

    weak_topics: list[str] = Field(
        default_factory=list,
        description="Topics that require further study."
    )

    performance_history: list[QuizPerformance] = Field(
        default_factory=list,
        description="Historical quiz performance."
    )