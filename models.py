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