from models import Route
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END

router_llm = ChatOllama(
    model="gemma4:e2b",
    temperature=0,
    num_predict=1000,
)
router = router_llm.with_structured_output(Route)

import operator

from typing import Annotated, TypedDict, Any

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
)

from models import (
    Quiz,
    StudentProfile,
    StudyPlan,
    PaperComparison,
)

from rag import (
    load_vector_store,
    get_llm,
    ask_tutor,
)

class LearningResearchState(TypedDict, total=False):

    # Student
    student_id: str

    # Conversation
    messages: Annotated[list[BaseMessage], operator.add]
    user_message: str

    # Supervisor
    next: str

    # Response
    response: str

    # Tutor
    retrieved_documents: list[Any]

    # Quiz
    quiz: Quiz
    student_answers: list[Any]

    # Evaluation
    evaluation: Any

    # Profile
    student_profile: StudentProfile

    # Planner
    study_plan: StudyPlan

    # Research
    research_response: str
    research_results: list[dict]

    # Comparison
    comparison: PaperComparison

    approval_status: str
    approval_request: str
    action_result: str


def create_initial_state(
    user_message: str,
    student_id: str = "student_001",
    **kwargs
):
    return {
        "student_id": student_id,
        "user_message": user_message,
        "messages": [
            HumanMessage(content=user_message)
        ],
        **kwargs,
    }

def tutor_node(state: LearningResearchState):

    question = state["user_message"]

    vector_store = load_vector_store()
    tutor_llm = get_llm()

    answer, documents = ask_tutor(
        vector_store=vector_store,
        llm=tutor_llm,
        question=question,
        k=5,
    )

    return {
        "response": answer,
        "retrieved_documents": documents,
        "messages": [
            AIMessage(content=answer)
        ],
    }

llm = ChatOllama(
    model="gemma4:e2b",
    temperature=0,
    num_predict=1000,
)
from rag import (
    load_vector_store,
    build_context,
    retrieve_documents
)

def build_quiz_prompt(
    context: str,
    topic: str,
    number_of_questions: int = 5
):
    return f"""
You are a university quiz generation assistant.

Generate a quiz based ONLY on the provided course context.

Topic:
{topic}

Number of questions:
{number_of_questions}

IMPORTANT RULES:

1. Use only information supported by the course context.
2. Do not invent concepts that are not present in the context.
3. Questions must test understanding, not only memorization.
4. Use a mixture of question types when appropriate.
5. Multiple-choice questions must contain clear choices.
6. The correct answer must be explicitly supported by the context.
7. Provide a concise explanation for every correct answer.
8. Make the questions appropriate for a university student.
9. Return exactly {number_of_questions} questions.
10. For multiple-choice questions, provide the choices in the choices field.
11. For true/false questions, use the correct_answer field appropriately.
12. For short-answer questions, choices must be an empty list.
13. Do not return Markdown.
14. Do not add introductory or concluding text.
15. Do not write "Correct Answer:" or "Explanation:" outside the corresponding structured fields.
16. Every question MUST contain a topic field.
17. The topic field of every question MUST be exactly:
    "{topic}"
18. Do not omit the topic field from any question.
19. Every question_id MUST be an integer.
20. question_id MUST NOT contain letters.
21. Do NOT use values such as "Q1", "Q2", "Q3", etc.
22. Use sequential integer values starting from 1:
    1, 2, 3, ..., {number_of_questions}.

COURSE CONTEXT:
----------------
{context}
----------------

Generate the quiz according to the required structured output schema.

The root output must be a Quiz object.

The output must contain:
- title
- topic
- questions

The root topic field must be:
"{topic}"

The questions field must contain exactly {number_of_questions} questions.

Do NOT return the questions as a standalone JSON array.

Each question MUST contain ALL of the following fields:
- question_id
- question
- topic
- question_type
- choices
- correct_answer
- explanation

For every question:

- question_id must be an integer.
- question_id must start at 1.
- question_id must increase sequentially.
- For {number_of_questions} questions, the question_id values must be:
  1, 2, 3, ..., {number_of_questions}.
- Never use "Q1", "Q2", "Q3" or any other string as question_id.
- topic must be exactly "{topic}".
- question must be based only on the course context.
- question_type must be one of the allowed values.
- choices must contain options only for multiple-choice questions.
- choices must be an empty list for true/false and short-answer questions.
- correct_answer must contain the correct answer.
- explanation must briefly explain why the answer is correct using information from the course context.

Use these exact question_type values:
- multiple_choice
- true_false
- short_answer

Return only the structured Quiz object.
"""

def generate_quiz(
    vector_store,
    quiz_llm,
    topic: str,
    number_of_questions: int = 5,
    k: int = 5
):
    documents = retrieve_documents(
        vector_store,
        topic,
        k=k
    )

    context = build_context(documents)

    prompt = build_quiz_prompt(
        context=context,
        topic=topic,
        number_of_questions=number_of_questions
    )

    quiz = quiz_llm.invoke(prompt)

    return quiz, documents

from models import Quiz
quiz_llm = llm.with_structured_output(Quiz)

def quiz_node(state: LearningResearchState):

    topic = state["user_message"]

    vector_store = load_vector_store()

    quiz, documents = generate_quiz(
        vector_store=vector_store,
        quiz_llm=quiz_llm,
        topic=topic,
        number_of_questions=5,
        k=5,
    )

    response = (
        f"Quiz generated successfully: "
        f"{quiz.title}"
    )

    return {
        "quiz": quiz,
        "retrieved_documents": documents,
        "response": response,
        "messages": [
            AIMessage(content=response)
        ],
    }

planner_llm = llm.with_structured_output(StudyPlan)

def build_planner_prompt(
    profile: StudentProfile,
    number_of_sessions: int = 3
):
    history = "\n".join(
        [
            (
                f"- {performance.quiz_title}: "
                f"{performance.percentage:.1f}% "
                f"(strong: {performance.strong_topics}, "
                f"weak: {performance.weak_topics})"
            )
            for performance in profile.performance_history
        ]
    )

    return f"""
You are a personalized learning planner for a university student.

Your task is to create an adaptive and personalized study plan based
ONLY on the student's information provided below.

====================
STUDENT PROFILE
====================

Student ID:
{profile.student_id}

Quizzes completed:
{profile.quizzes_completed}

Average score:
{profile.average_score:.2f}

Average percentage:
{profile.average_percentage:.2f}%

Strong topics:
{profile.strong_topics}

Weak topics:
{profile.weak_topics}

====================
PERFORMANCE HISTORY
====================

{history}

====================
PLANNING REQUIREMENTS
====================

1. Create EXACTLY {number_of_sessions} study sessions.

2. Prioritize weak topics over strong topics.

3. Give HIGH priority to weak topics whenever appropriate.

4. Strong topics should receive less study time and should mainly be
   used for maintenance or quick review.

5. Use the student's performance history to adapt the study plan.

6. If a topic repeatedly appears as a weak topic or has low quiz
   performance, give it more attention.

7. The plan should be progressive:
   - begin with reviewing or understanding concepts,
   - continue with practice and application,
   - finish with evaluation or self-assessment whenever appropriate.

8. Each study session must contain:
   - session_number
   - topic
   - objective
   - activities
   - priority
   - estimated_minutes

9. Activities must be concrete and appropriate for a university student.

10. Do NOT invent specific course content, chapters, concepts,
    exercises, technologies, or subjects that are not present in the
    student's profile or performance history.

11. If there are not enough weak topics to fill all sessions, use
    strong topics for maintenance, but give them lower priority and
    shorter study time.

12. The overall goal must summarize what the student should achieve
    through the complete study plan.

13. The plan_summary must briefly explain why the selected topics,
    priorities, and progression were chosen based on the student's
    performance.

====================
OUTPUT FORMAT
====================

Your response MUST be a valid JSON object that matches EXACTLY the
following structure:

{{
  "student_id": "{profile.student_id}",
  "overall_goal": "Overall learning goal of the study plan.",
  "sessions": [
    {{
      "session_number": 1,
      "topic": "Topic name",
      "objective": "Learning objective for this session.",
      "activities": [
        "Activity 1",
        "Activity 2",
        "Activity 3"
      ],
      "priority": "high",
      "estimated_minutes": 60
    }},
    {{
      "session_number": 2,
      "topic": "Topic name",
      "objective": "Learning objective for this session.",
      "activities": [
        "Activity 1",
        "Activity 2",
        "Activity 3"
      ],
      "priority": "medium",
      "estimated_minutes": 45
    }},
    {{
      "session_number": 3,
      "topic": "Topic name",
      "objective": "Learning objective for this session.",
      "activities": [
        "Activity 1",
        "Activity 2",
        "Activity 3"
      ],
      "priority": "low",
      "estimated_minutes": 30
    }}
  ],
  "plan_summary": "Short explanation of why this study plan was created."
}}

====================
STRICT JSON RULES
====================

The output MUST follow these rules:

1. Return ONLY the JSON object.

2. Do NOT write anything before the JSON.

3. Do NOT write anything after the JSON.

4. Do NOT use Markdown.

5. Do NOT use ```json or ``` code fences.

6. Do NOT include comments.

7. Use double quotes for all JSON keys and string values.

8. Do NOT use trailing commas.

9. The top-level JSON object MUST contain exactly these four fields:
   - student_id
   - overall_goal
   - sessions
   - plan_summary

10. Each session MUST contain exactly these six fields:
    - session_number
    - topic
    - objective
    - activities
    - priority
    - estimated_minutes

11. "student_id" MUST be exactly:
    "{profile.student_id}"

12. "sessions" MUST contain EXACTLY {number_of_sessions} session objects.

13. "session_number" must be an integer.

14. "topic" must be a string.

15. "objective" must be a string.

16. "activities" must be an array of strings.

17. "priority" MUST be exactly one of:
    "high"
    "medium"
    "low"

18. "estimated_minutes" must be an integer greater than or equal to 5.

19. "overall_goal" must be a string.

20. "plan_summary" must be a string.

21. Do not add any additional fields.

Before returning the answer, internally verify that:
- the response is valid JSON,
- all required fields are present,
- no extra fields are present,
- exactly {number_of_sessions} sessions are present,
- every session contains all six required fields,
- every priority value is either "high", "medium", or "low",
- every estimated_minutes value is at least 5.

Now generate the personalized study plan.
"""

def generate_study_plan(
    profile: StudentProfile,
    planner_llm,
    number_of_sessions: int = 3
):
    prompt = build_planner_prompt(
        profile=profile,
        number_of_sessions=number_of_sessions
    )

    study_plan = planner_llm.invoke(prompt)

    return study_plan

def planner_node(state: LearningResearchState):

    profile = state.get("student_profile")

    if profile is None:

        response = (
            "No student profile is available yet. "
            "Complete at least one learning activity "
            "so that a personalized study plan can be generated."
        )

        return {
            "response": response,
            "messages": [
                AIMessage(content=response)
            ],
        }

    study_plan = generate_study_plan(
        profile=profile,
        planner_llm=planner_llm,
        number_of_sessions=3,
    )

    response = (
        f"Study plan generated successfully "
        f"for student {study_plan.student_id}."
    )

    return {
        "study_plan": study_plan,
        "response": response,
        "messages": [
            AIMessage(content=response)
        ],
    }

from langchain.agents.middleware import (
    wrap_model_call,
    wrap_tool_call,
)
from langchain_core.messages import ToolMessage

@wrap_model_call
def model_logging(request, handler):
    print("[Middleware] Appel du modèle en cours...")

    response = handler(request)

    print("[Middleware] Appel du modèle terminé.")

    return response

@wrap_tool_call
def tool_guard(request, handler):

    tool_name = request.tool_call["name"]
    tool_args = request.tool_call["args"]

    print(f"[Middleware] Outil demandé : {tool_name}")

    if tool_name == "web_fetch":

        url = tool_args.get("url", "")
        allowed_prefixes = ("https://", "http://")

        if not url.startswith(allowed_prefixes):
            return ToolMessage(
                content="Blocked: only HTTP and HTTPS URLs are allowed.",
                tool_call_id=request.tool_call["id"],
                name=tool_name,
                status="error",
            )

    return handler(request)
@wrap_model_call
def input_guardrail(request, handler):

    # Trouver le dernier message utilisateur
    user_messages = [
        message
        for message in request.messages
        if isinstance(message, HumanMessage)
    ]

    if not user_messages:
        return handler(request)

    user_text = user_messages[-1].content

    # Notre contrôle traite ici du texte simple
    if not isinstance(user_text, str):
        return AIMessage(
            content="Please submit your request as text."
        )

    # Limiter la taille de la requête
    if len(user_text) > 10000:
        return AIMessage(
            content=(
                "Your request is too long. "
                "Please shorten it to 10,000 characters or fewer."
            )
        )

    if not user_text.strip():
        return AIMessage(
            content="Please enter a non-empty request."
        )

    # Détection élémentaire de quelques formulations d'injection
    suspicious_phrases = [
        "ignore all previous instructions",
        "ignore your system prompt",
        "reveal your system prompt",
        "show me your api key",
    ]

    normalized_text = user_text.lower()

    if any(
        phrase in normalized_text
        for phrase in suspicious_phrases
    ):
        return AIMessage(
            content=(
                "I can't follow instructions that attempt "
                "to override system rules or reveal secrets. "
                "Please ask a question about your course "
                "or scientific research."
            )
        )

    # Si aucune règle ne bloque la demande, continuer
    return handler(request)

from langchain.agents import create_agent
from tools import web_search, web_fetch
research_tools = [
    web_search,
    web_fetch,
]

research_agent = create_agent(
    model=llm,
    tools=research_tools,
    system_prompt="""
You are a scientific research assistant.

Your role is to help students research scientific and
technical topics using reliable web sources.

You have access to two tools:

- web_search: search the web for relevant information.
- web_fetch: retrieve the content of a web page.

Rules:

1. Use web_search when the user asks for current,
   external, or scientific information that is not
   available in the student's course documents.

2. Use web_fetch when you need more information from
   a specific source found during the search.

3. Prefer relevant and trustworthy sources.

4. Clearly distinguish information obtained from web
   sources from information already available in the
   student's course material.

5. Do not invent sources, URLs, authors, or scientific
   results.

6. When possible, mention the sources used.

7. Give clear and structured answers suitable for a
   university student.
""", 
    middleware=[
        input_guardrail,
        model_logging,
        tool_guard,
    ],
)

def extract_research_papers(messages):

    papers = []

    for message in messages:

        if message.__class__.__name__ != "ToolMessage":
            continue

        content = message.content

        if isinstance(content, list):

            for item in content:

                if isinstance(item, dict):

                    if "url" in item:
                        papers.append(item)

        elif isinstance(content, dict):

            if "url" in content:
                papers.append(content)

    return papers

import re

def validate_and_sanitize_output(text: str) -> str:

    if not isinstance(text, str) or not text.strip():
        return (
            "The assistant could not produce a valid response. "
            "Please try again."
        )

    # Masquer certaines clés ressemblant à des clés API
    text = re.sub(
        r"\bsk-[A-Za-z0-9_-]{12,}\b",
        "[REDACTED_API_KEY]",
        text,
    )

    # Limiter la taille de la réponse présentée
    max_output_length = 20000

    if len(text) > max_output_length:
        text = (
            text[:max_output_length]
            + "\n\n[Response truncated]"
        )

    return text

def research_node(state: LearningResearchState):

    user_message = state["user_message"]

    result = research_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_message,
                }
            ]
        }
    )

    messages = result["messages"]

    """final_response = ""

    for message in reversed(messages):

        if isinstance(message, AIMessage):

            if message.content:
                final_response = message.content
                break"""
    
    final_response = ""

    for message in reversed(messages):

        if isinstance(message, AIMessage):

            # Ignorer les messages qui demandent l'exécution d'un outil
            if getattr(message, "tool_calls", None):
                 continue

            if isinstance(message.content, str) and message.content.strip():
                final_response = message.content
                break
            if message.content and not isinstance(message.content, str):
                final_response = str(message.content)
                break

    final_response = validate_and_sanitize_output(
         final_response
    )

    papers = extract_research_papers(messages)
    
    compare_requested = any(
    word in user_message.lower()
    for word in [
        "compare",
        "comparison",
        "comparaison",
        "comparer",
    ]
    )

    next_step = (
    "comparison"
    if compare_requested and len(papers) >= 2
    else "FINISH"
    )

    return {
        "research_response": final_response,
        "research_results": papers,
        "response": final_response,
        "next": next_step,
        "messages": [
            AIMessage(content=final_response)
        ],
    }

comparison_llm = llm.with_structured_output(PaperComparison)

def build_comparison_prompt(
    papers_context: str,
    research_question: str
):
    return f"""
You are a scientific paper comparison assistant.

Your task is to analyze and compare scientific papers using ONLY
the information provided in the paper context.

====================
RESEARCH QUESTION
====================

{research_question}

====================
PAPERS
====================

{papers_context}

====================
ANALYSIS REQUIREMENTS
====================

1. Analyze all papers provided in the context.

2. Extract a structured summary for each paper, including:
   - title
   - authors
   - year
   - research_problem
   - methodology
   - dataset
   - main_results
   - strengths
   - limitations

3. Identify important similarities and differences between the papers.

4. Compare their research problems, methodologies, datasets,
   reported results, strengths, and limitations.

5. Compare numerical results only when the evaluation metrics,
   datasets, and experimental settings are sufficiently comparable.

6. If results cannot be compared directly, explain why.

7. Use only information supported by the provided context.
   Do not invent authors, publication years, datasets, methods,
   numerical results, strengths, or limitations.

8. Distinguish explicitly reported facts from reasonable
   interpretations based on the provided information.

9. If information is missing, state "Not available in the provided
   context." for string fields. For list fields, use an empty list
   when no reliable information is available.

10. Preserve the original meaning of the papers. Do not exaggerate
    their contributions or claim that one approach is superior
    without supporting evidence.

11. The overall conclusion MUST directly answer the research question.

12. Provide a concise but informative scientific comparison.

====================
STRICT OUTPUT FORMAT
====================

Return ONLY one valid JSON object compatible with the
PaperComparison Pydantic model.

The top-level object MUST contain exactly these seven fields:

- papers
- comparison_points
- methodology_comparison
- results_comparison
- strengths_comparison
- limitations_comparison
- overall_conclusion

The "papers" field MUST be an array containing one PaperSummary
object for EACH paper provided in the context.

Each PaperSummary object MUST contain exactly these nine fields:

- title: string
- authors: array of strings
- year: string
- research_problem: string
- methodology: string
- dataset: string
- main_results: string
- strengths: array of strings
- limitations: array of strings

The other fields MUST have the following types:

- comparison_points: array of strings
- methodology_comparison: string
- results_comparison: string
- strengths_comparison: string
- limitations_comparison: string
- overall_conclusion: string

====================
JSON TEMPLATE
====================

Use the following structure as a guide. Replace all example values
with information grounded in the provided papers.

{{
  "papers": [
    {{
      "title": "Paper title",
      "authors": ["Author name"],
      "year": "Publication year",
      "research_problem": "Research problem addressed",
      "methodology": "Methodology used",
      "dataset": "Dataset or data used",
      "main_results": "Main reported results",
      "strengths": ["Evidence-supported strength"],
      "limitations": ["Evidence-supported limitation"]
    }}
  ],
  "comparison_points": [
    "Important similarity or difference between the papers"
  ],
  "methodology_comparison": "Compare the methodologies.",
  "results_comparison": "Compare the reported results and explain any limitations to direct comparison.",
  "strengths_comparison": "Compare the supported strengths.",
  "limitations_comparison": "Compare the supported limitations.",
  "overall_conclusion": "Answer the research question using evidence from the papers."
}}

====================
STRICT JSON RULES
====================

1. Return ONLY the JSON object.
2. Do not include Markdown or Markdown headings.
3. Do not use ```json or any other code fences.
4. Do not write introductory text before the JSON.
5. Do not write explanations after the JSON.
6. Use double quotes for all keys and string values.
7. Do not use trailing commas.
8. Do not include comments in the JSON.
9. Use [] for unavailable list fields; never use null.
10. Use strings for all string fields; never use null.
11. Do not add fields that are not defined in PaperComparison
    or PaperSummary.
12. Include every required field, even when information is missing.
13. The "papers" array must include all papers supplied in the context.
14. Ensure every paper summary follows the exact PaperSummary schema.

Before responding, verify that the output is valid JSON and that
all required fields and data types match the specified schema.

Now generate the scientific paper comparison.
"""

def build_papers_context(papers: list[dict]) -> str:
    """Convert retrieved paper dictionaries into readable comparison context."""
    if not papers:
        return "No structured paper details were available."

    sections = []
    for index, paper in enumerate(papers, start=1):
        if not isinstance(paper, dict):
            continue
        lines = [f"Paper {index}"]
        for key, value in paper.items():
            lines.append(f"{key}: {value}")
        sections.append("\n".join(lines))

    return "\n\n---\n\n".join(sections)


def compare_papers(
    papers: list[dict],
    research_question: str,
    comparison_llm
):
    papers_context = build_papers_context(papers)

    prompt = build_comparison_prompt(
        papers_context=papers_context,
        research_question=research_question
    )

    comparison = comparison_llm.invoke(prompt)

    return comparison

def comparison_node(state: LearningResearchState):

    papers = state.get("research_results", [])

    if len(papers) < 2:

        response = (
            "At least two structured research papers "
            "are required for comparison."
        )

        return {
            "response": response,
            "messages": [
                AIMessage(content=response)
            ],
        }

    research_question = state["user_message"]

    comparison = compare_papers(
        papers=papers,
        research_question=research_question,
        comparison_llm=comparison_llm,
    )

    response = comparison.overall_conclusion

    return {
        "comparison": comparison,
        "response": response,
        "messages": [
            AIMessage(content=response)
        ],
    }

from langgraph.types import interrupt


def plan_approval_node(state: LearningResearchState) -> dict:
    # Ne rien demander si aucun plan n'a été produit.
    plan = state.get("study_plan")

    if plan is None:
        return {
            "approval_status": "not_required",
            "action_result": "Aucun plan à valider."
        }

    # Préparer un aperçu textuel du plan.
    if hasattr(plan, "model_dump_json"):
        plan_preview = plan.model_dump_json(indent=2)
    else:
        plan_preview = str(plan)

    # Suspendre le workflow pour demander l'avis de l'étudiant.
    decision = interrupt({
        "question": "Voulez-vous accepter ce plan de révision ?",
        "plan": plan_preview,
        "choices": ["approve", "reject"]
    })

    if decision == "approve":
        return {
            "approval_status": "approved",
            "action_result": (
                "Le plan de révision a été approuvé "
                "par l'étudiant."
            ),
            "response": (
                plan_preview
                + "\n\nStatut : plan approuvé par l'étudiant."
            )
        }

    if decision == "reject":
        return {
            "approval_status": "rejected",
            "action_result": (
                "Le plan a été refusé. "
                "Il n'est pas considéré comme accepté."
            ),
            "response": (
                plan_preview
                + "\n\nStatut : plan refusé par l'étudiant."
            )
        }

    return {
        "approval_status": "invalid_decision",
        "action_result": (
            "Décision invalide. "
            "Le plan n'est pas considéré comme accepté."
        )
    }

SUPERVISOR_PROMPT = """
You are the supervisor of a multi-agent personal learning and research assistant.

Your responsibility is to route each user request to exactly one specialized agent.

Available agents:

tutor:
- Explains concepts from the student's course.
- Answers questions using the RAG course knowledge base.
- Handles questions such as "Explain TCP", "What is a semaphore?", or "Explain this course concept."

quiz:
- Generates quizzes based on course content.
- Creates questions and choices from the student's course material.

evaluation:
- Evaluates a student's quiz answers.
- Analyzes quiz performance.
- Identifies mistakes, weak areas, and performance.

planner:
- Creates personalized study plans.
- Uses the student's profile, performance, weak topics, and learning goals.

research:
- Searches the web for scientific information and papers.
- Uses web search and web fetch.
- Handles requests requiring recent or external scientific information.

comparison:
- Compares scientific papers.
- Produces structured comparisons of methodologies, results, strengths, and limitations.

FINISH:
- Use only when the request has already been completed or when no specialized agent is necessary.

Routing rules:

1. Questions about concepts from the student's course should go to tutor.

2. Requests to generate a quiz based on course content should go to quiz.

3. Requests to evaluate quiz answers or analyze quiz performance should go to evaluation.

4. Requests for personalized study plans should go to planner.

5. Requests requiring recent scientific information, web research, or scientific papers should go to research.

6. Requests to compare two or more scientific papers should go to comparison.

7. Choose exactly ONE agent.

8. Do not answer the user's request yourself.

9. The "next" field MUST contain exactly one of:
   - "tutor"
   - "quiz"
   - "evaluation"
   - "planner"
   - "research"
   - "comparison"
   - "FINISH"

10. The "reason" field MUST contain a short explanation of why the selected agent is appropriate.

11. Return ONLY a valid JSON object.

12. Do NOT return Markdown.

13. Do NOT use code fences.

14. Do NOT return text such as:
   "NEXT AGENT: tutor"
   "The next agent is tutor"
   "Agent: tutor"

15. The JSON object MUST have exactly these two fields:
   "next" and "reason".

16. The value of "next" must be one of the allowed agent names listed above.

17. The "reason" should be concise and should explain the routing decision.

18. Research and comparison rule:
     - If the user asks to compare scientific papers and no research
  sources are currently available, route to research first.
     - If research sources are already available and the user asks
  for a comparison, route to comparison.
  
Expected output format:

{
    "next": "tutor",
    "reason": "The request asks for an explanation of a course concept."
}
"""

def route_request(
    user_message: str,
    has_research_results: bool = False,
):

    research_status = (
        "Research sources are already available."
        if has_research_results
        else "No research sources are currently available."
    )

    messages = [
        {
            "role": "system",
            "content": SUPERVISOR_PROMPT
            + f"\n\nCurrent state:\n{research_status}"
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    return router.invoke(messages)

def supervisor_node(state: LearningResearchState):

    decision = route_request(
        user_message=state["user_message"],
        has_research_results=bool(
            state.get("research_results")
        ),
    )

    return {
        "next": decision.next
    }

from models import (
    QuestionEvaluation,
    QuizEvaluation,
    StudentAnswer
)
evaluation_llm = llm.with_structured_output(QuizEvaluation)

def build_evaluation_prompt(
    quiz: Quiz,
    student_answers: list[StudentAnswer]
):
    quiz_data = "\n\n".join(
        [
            f"""
Question ID: {question.question_id}
Question: {question.question}
Type: {question.question_type}
Choices: {question.choices}
Correct answer: {question.correct_answer}
Topic: {question.topic}
Explanation: {question.explanation}
"""
            for question in quiz.questions
        ]
    )

    answers_data = "\n\n".join(
        [
            f"""
Question ID: {answer.question_id}
Student answer: {answer.answer}
"""
            for answer in student_answers
        ]
    )

    return f"""
You are an educational evaluation assistant.

Your task is to evaluate a student's answers to a university quiz.

QUIZ
====
Title: {quiz.title}
Main topic: {quiz.topic}

{quiz_data}

STUDENT ANSWERS
===============
{answers_data}

EVALUATION RULES
================

1. Evaluate every question in the quiz.
2. Match each student answer to the question using question_id.
3. Compare the student's answer with the correct answer provided in the quiz.
4. For multiple-choice questions, consider the answer correct only if it
   corresponds to the provided correct answer.
5. For true/false questions, compare the student's answer with the provided
   correct answer.
6. For short-answer questions, evaluate the meaning and correctness of the
   student's answer, not only the exact wording.
7. Do not use knowledge that is not supported by the quiz information.
8. Give a score between 0 and 1 for every question.
9. A fully correct answer should receive a score of 1.
10. A completely incorrect answer should receive a score of 0.
11. A partially correct short-answer response may receive a score between
    0 and 1.
12. Set is_correct to true only when the answer is sufficiently correct.
13. Provide short and clear pedagogical feedback for every question.
14. Identify the topics the student understands well.
15. Identify the topics the student needs to review.
16. Calculate the total score from the individual question scores.
17. Calculate the percentage based on the total score.
18. Count the number of correctly answered questions.
19. Return exactly one QuestionEvaluation for every quiz question.
20. Preserve the original question_id for every question.
21. Preserve the student's answer exactly in student_answer.
22. Use the provided correct answer in correct_answer.
23. Use the topic provided for each question.
24. quiz_title must be exactly the title of the quiz.
25. total_questions must equal the number of questions in the quiz.
26. correct_answers must equal the number of questions where is_correct is true.
27. score must represent the total score obtained from all questions.
28. percentage must represent the score as a percentage from 0 to 100.

OUTPUT FORMAT
=============

Return ONLY one JSON object corresponding to the QuizEvaluation schema.

The output must contain these top-level fields:

- quiz_title
- total_questions
- correct_answers
- score
- percentage
- strong_topics
- weak_topics
- question_results
- overall_feedback

Each object inside question_results MUST contain:

- question_id
- student_answer
- correct_answer
- is_correct
- score
- feedback
- topic

The question_results list MUST contain exactly {len(quiz.questions)} elements.

There must be exactly one QuestionEvaluation object for each quiz question.

IMPORTANT OUTPUT RESTRICTIONS:

- Return ONLY the JSON object.
- Do NOT return Markdown.
- Do NOT use ```json.
- Do NOT use ``` or code fences.
- Do NOT write any introduction before the JSON.
- Do NOT write any conclusion after the JSON.
- Do NOT add bullet points outside the JSON.
- Do NOT add recommendations outside the JSON.
- Do NOT add explanations outside the JSON.
- All feedback, recommendations, and evaluation comments must be placed
  inside the appropriate JSON fields.
- The JSON must be valid and parseable.
- Use double quotes for JSON strings.
- Do not add trailing commas.

Return ONLY the structured QuizEvaluation JSON object.
"""

def evaluate_quiz(
    quiz: Quiz,
    student_answers: list[StudentAnswer],
    evaluation_llm
):
    prompt = build_evaluation_prompt(
        quiz=quiz,
        student_answers=student_answers
    )

    evaluation = evaluation_llm.invoke(prompt)

    return evaluation


def evaluation_node(state: LearningResearchState):
    """Evaluate the student's answers to the quiz."""

    quiz = state.get("quiz")
    student_answers = state.get("student_answers", [])

    # Vérifier que le quiz est disponible
    if quiz is None:
        response = (
            "No quiz is available for evaluation. "
            "Please generate a quiz before submitting your answers."
        )
        return {
            "response": response,
            "messages": [AIMessage(content=response)],
        }

    # Vérifier que les réponses sont disponibles
    if not student_answers:
        response = (
            "No student answers are available. "
            "Please submit your answers before requesting an evaluation."
        )
        return {
            "response": response,
            "messages": [AIMessage(content=response)],
        }

    try:
        # Évaluer les réponses avec l'évaluateur existant
        evaluation = evaluate_quiz(
            quiz=quiz,
            student_answers=student_answers,
            evaluation_llm=evaluation_llm,
        )

        # Enregistrer le résultat de l'évaluation
        if hasattr(evaluation, "model_dump"):
            evaluation_data = evaluation.model_dump()
            response = (
                f"Quiz evaluation completed successfully!\n\n"
                f"Quiz: {evaluation.quiz_title}\n"
                f"Score: {evaluation.score}\n"
                f"Percentage: {evaluation.percentage:.2f}%\n"
                f"Correct answers: {evaluation.correct_answers}/"
                f"{evaluation.total_questions}\n\n"
                f"Strong topics: {evaluation.strong_topics}\n"
                f"Weak topics: {evaluation.weak_topics}\n\n"
                f"Feedback: {evaluation.overall_feedback}"
            )
        else:
            evaluation_data = evaluation
            response = str(evaluation)

        return {
            "evaluation": evaluation,
            "response": response,
            "messages": [AIMessage(content=response)],
        }

    except Exception as e:
        response = (
            "An error occurred while evaluating the quiz: "
            f"{str(e)}"
        )
        return {
            "response": response,
            "messages": [AIMessage(content=response)],
        }


graph_builder = StateGraph(
    LearningResearchState
)
graph_builder.add_node(
    "supervisor",
    supervisor_node
)

graph_builder.add_node(
    "tutor",
    tutor_node
)

graph_builder.add_node(
    "quiz",
    quiz_node
)

graph_builder.add_node(
    "evaluation",
    evaluation_node
)

graph_builder.add_node(
    "planner",
    planner_node
)

graph_builder.add_node(
    "research",
    research_node
)

graph_builder.add_node(
    "comparison",
    comparison_node
)

graph_builder.add_node(
    "plan_approval",
    plan_approval_node
)

graph_builder.add_edge(
    START,
    "supervisor"
)
graph_builder.add_conditional_edges(
    "supervisor",
    lambda state: state["next"],
    {
        "tutor": "tutor",
        "quiz": "quiz",
        "evaluation": "evaluation",
        "planner": "planner",
        "research": "research",
        "comparison": "comparison",
        "FINISH": END,
    }
)
graph_builder.add_edge(
    "tutor",
    END
)

graph_builder.add_edge(
    "quiz",
    END
)

graph_builder.add_edge(
    "evaluation",
    END
)

"""graph_builder.add_edge(
    "planner",
    END
)"""
graph_builder.add_edge("planner", "plan_approval")
graph_builder.add_edge("plan_approval", END)

def route_after_research(state: LearningResearchState):

    return state.get("next", "FINISH")

graph_builder.add_conditional_edges(
    "research",
    route_after_research,
    {
        "comparison": "comparison",
        "FINISH": END,
    }
)

graph_builder.add_edge(
    "comparison",
    END
)

def make_config(thread_id: str):

    return {
        "configurable": {
            "thread_id": thread_id
        }
    }

from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()
learning_graph = graph_builder.compile(
    checkpointer=memory
)



