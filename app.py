import uuid
from pathlib import Path

import streamlit as st
from langgraph.types import Command

from graph import learning_graph, create_initial_state, make_config

st.set_page_config(
    page_title="Personal Learning Assistant",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 Personal Learning & Research Assistant")
st.caption(
    "Posez des questions sur vos cours, générez des quiz, "
    "préparez vos révisions et explorez la littérature scientifique."
)

# ---------------- Session ----------------
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "config" not in st.session_state:
    st.session_state.config = make_config(st.session_state.thread_id)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_interrupt" not in st.session_state:
    st.session_state.pending_interrupt = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "student_profile" not in st.session_state:
    st.session_state.student_profile = None


def as_dict(value):
    """Convert Pydantic objects into dictionaries for display."""
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, dict):
        return value
    return None


def show_structured_result(result):
    """Render quiz, study plan, comparison and research outputs."""
    if not result:
        return

    quiz = as_dict(result.get("quiz"))
    if quiz:
        st.subheader(quiz.get("title", "Quiz"))
        if quiz.get("topic"):
            st.caption(f"Sujet : {quiz['topic']}")
        for index, question in enumerate(quiz.get("questions", []), start=1):
            with st.expander(
                f"Question {question.get('question_id', index)} — "
                f"{question.get('question', '')}",
                expanded=True,
            ):
                choices = question.get("choices") or []
                if choices:
                    for choice in choices:
                        st.markdown(f"- {choice}")
                st.caption(
                    f"Type : {question.get('question_type', 'non précisé')}"
                )
                with st.expander("Afficher la correction"):
                    st.markdown(
                        f"**Réponse :** {question.get('correct_answer', 'Non fournie')}"
                    )
                    st.write(question.get("explanation", ""))

    plan = as_dict(result.get("study_plan"))
    if plan:
        st.subheader("Plan de révision")
        st.write(plan.get("overall_goal", ""))
        st.info(plan.get("plan_summary", ""))
        for session in plan.get("sessions", []):
            with st.expander(
                f"Session {session.get('session_number', '?')} — "
                f"{session.get('topic', 'Sujet')}"
            ):
                st.write(session.get("objective", ""))
                st.write("**Activités**")
                for activity in session.get("activities", []):
                    st.markdown(f"- {activity}")
                st.write(
                    f"Priorité : {session.get('priority', '—')} · "
                    f"Durée estimée : {session.get('estimated_minutes', '—')} min"
                )

    comparison = as_dict(result.get("comparison"))
    if comparison:
        st.subheader("Comparaison scientifique")
        st.write(comparison.get("overall_conclusion", ""))
        for field, label in [
            ("methodology_comparison", "Méthodologies"),
            ("results_comparison", "Résultats"),
            ("strengths_comparison", "Points forts"),
            ("limitations_comparison", "Limites"),
        ]:
            if comparison.get(field):
                with st.expander(label):
                    st.write(comparison[field])
        if comparison.get("comparison_points"):
            st.markdown("**Points de comparaison**")
            for point in comparison["comparison_points"]:
                st.markdown(f"- {point}")

    papers = result.get("research_results") or []
    if papers:
        st.subheader("Sources structurées récupérées")
        for index, paper in enumerate(papers, start=1):
            if isinstance(paper, dict):
                with st.expander(paper.get("title", f"Source {index}")):
                    st.json(paper)

    evaluation = result.get("evaluation")
    if evaluation is not None:
        st.subheader("Évaluation")
        st.write(evaluation)


def process_graph_result(result):
    st.session_state.last_result = result
    interruptions = result.get("__interrupt__", [])
    if interruptions:
        st.session_state.pending_interrupt = interruptions[0].value
        return

    st.session_state.pending_interrupt = None
    response = result.get("response", "")
    if not response and result.get("action_result"):
        response = result["action_result"]
    if not response:
        response = (
            "Le workflow est terminé. Consultez les résultats structurés "
            "ci-dessous si un quiz, un plan ou une comparaison a été produit."
        )
    st.session_state.messages.append(
        {"role": "assistant", "content": str(response)}
    )


def start_new_conversation():
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.config = make_config(st.session_state.thread_id)
    st.session_state.messages = []
    st.session_state.pending_interrupt = None
    st.session_state.last_result = None


# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("Navigation")
    mode = st.selectbox(
        "Type de demande",
        [
            "Routage automatique",
            "Tuteur de cours",
            "Générer un quiz",
            "Plan de révision",
            "Recherche scientifique",
            "Comparer des articles",
        ],
    )

    st.divider()
    st.subheader("Profil étudiant")
    st.write(
        "Le graphe accepte un `StudentProfile` existant. "
        "La création et la persistance du profil seront connectées "
        "à votre modèle `StudentProfile` dans une étape dédiée."
    )
    if st.session_state.student_profile is None:
        st.caption("Aucun profil chargé dans cette session.")

    st.divider()
    st.caption("Identifiant de session")
    st.code(st.session_state.thread_id[:8])
    if st.button("Nouvelle conversation", use_container_width=True):
        start_new_conversation()
        st.rerun()


# ---------------- PDF upload / preview ----------------
with st.expander("📄 Importer un PDF de cours", expanded=False):
    uploaded_pdf = st.file_uploader(
        "Choisissez un PDF à analyser",
        type=["pdf"],
        key="course_pdf_uploader",
    )
    st.caption(
        "Cette section extrait et prévisualise le texte avec Docling. "
        "Le PDF n'est pas encore ajouté automatiquement à FAISS ; "
        "il ne sera donc pas utilisé par le tuteur RAG tant que "
        "l'indexation n'est pas reliée à votre fonction dans rag.py."
    )
    if uploaded_pdf is not None:
        if st.button("Extraire le texte du PDF", key="extract_pdf"):
            try:
                from docling.document_converter import DocumentConverter

                temp_dir = Path("data") / "courses" / "uploads"
                temp_dir.mkdir(parents=True, exist_ok=True)
                temp_path = temp_dir / uploaded_pdf.name
                temp_path.write_bytes(uploaded_pdf.getvalue())

                with st.spinner("Extraction du PDF avec Docling..."):
                    converter = DocumentConverter()
                    converted = converter.convert(str(temp_path))
                    extracted_text = converted.document.export_to_text()

                st.success(
                    f"Extraction terminée : {len(extracted_text)} caractères."
                )
                st.text_area(
                    "Aperçu du texte extrait",
                    extracted_text[:15000],
                    height=300,
                )
                st.session_state.extracted_course_text = extracted_text
                st.session_state.extracted_course_path = str(temp_path)
            except Exception as exc:
                st.error("Impossible d'extraire ce PDF avec Docling.")
                st.exception(exc)


# ---------------- Chat history ----------------
for item in st.session_state.messages:
    with st.chat_message(item["role"]):
        st.markdown(item["content"])


# ---------------- Human in the loop ----------------
pending = st.session_state.pending_interrupt
if pending:
    st.warning("⏸️ Le workflow attend votre décision.")
    st.markdown(pending.get("question", "Veuillez confirmer cette action."))

    if pending.get("plan"):
        with st.expander("Consulter le plan proposé", expanded=True):
            st.code(pending["plan"], language="json")
    elif pending.get("action"):
        st.write("Action proposée :", pending["action"])

    approve_col, reject_col = st.columns(2)
    with approve_col:
        if st.button("✅ Approuver", type="primary", use_container_width=True):
            try:
                resumed = learning_graph.invoke(
                    Command(resume="approve"),
                    config=st.session_state.config,
                )
                process_graph_result(resumed)
                st.rerun()
            except Exception as exc:
                st.error("La reprise du workflow a échoué.")
                st.exception(exc)

    with reject_col:
        if st.button("❌ Refuser", use_container_width=True):
            try:
                resumed = learning_graph.invoke(
                    Command(resume="reject"),
                    config=st.session_state.config,
                )
                process_graph_result(resumed)
                st.rerun()
            except Exception as exc:
                st.error("La reprise du workflow a échoué.")
                st.exception(exc)


# ---------------- Chat input ----------------
if not st.session_state.pending_interrupt:
    prompt = st.chat_input(
        "Ex. : explique TCP, génère un quiz sur les protocoles..."
    )

    if prompt:
        st.session_state.messages.append(
            {"role": "user", "content": prompt}
        )
        with st.chat_message("user"):
            st.markdown(prompt)

        routing_prefix = {
            "Routage automatique": "",
            "Tuteur de cours": "Explain the following course question using the course documents: ",
            "Générer un quiz": "Generate a quiz based on the course documents about: ",
            "Plan de révision": "Create a personalized study plan for the student. Request: ",
            "Recherche scientifique": "Research this scientific topic using web sources: ",
            "Comparer des articles": "Compare scientific papers about this topic. If sources are not available, research them first: ",
        }
        graph_prompt = routing_prefix[mode] + prompt

        try:
            initial_state = create_initial_state(
                user_message=graph_prompt,
                student_id="student_001",
            )
            # Inject an existing profile only if the application has one.
            profile = st.session_state.student_profile
            if profile is not None:
                initial_state["student_profile"] = profile

            with st.chat_message("assistant"):
                with st.spinner("Les agents analysent votre demande..."):
                    result = learning_graph.invoke(
                        initial_state,
                        config=st.session_state.config,
                    )
                process_graph_result(result)

                if st.session_state.pending_interrupt:
                    st.info("Le workflow est suspendu en attendant votre décision.")
                else:
                    response = result.get("response", "")
                    if response:
                        st.markdown(str(response))
                    show_structured_result(result)

        except Exception as exc:
            st.error("Une erreur est survenue pendant l'exécution du workflow.")
            st.exception(exc)

# Show structured output again after reruns, except while a new prompt is being handled.
if st.session_state.last_result and not st.session_state.pending_interrupt:
    with st.expander("Voir les résultats structurés du dernier traitement", expanded=False):
        show_structured_result(st.session_state.last_result)
