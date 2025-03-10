from langchain_openai.chat_models import ChatOpenAI
from app.chat.models import ChatArgs
from app.chat.vector_stores import retriever_map
from app.chat.llms import llm_map
from app.chat.memories import memory_map
from app.chat.chains.retrieval import StreamingConversationalRetrievalChain 
from app.web.api import (
    get_conversation_components,
    set_conversation_components
)
from app.chat.score import random_component_by_score

def select_component(component_type, component_map, chat_args):
    """
    :param component_type: str, the type of component to select
    :param component_map: dict, a map of component types to component classes
    :param chat_args: ChatArgs object containing
        conversation_id, pdf_id, metadata, and streaming flag.

    :return: An instance of the component class

    Example Usage:

        retriever = select_component(
            component_type="retriever",
            component_map=retriever_map,
            chat_args=chat_args
        )
    """
    component_class = get_conversation_components(chat_args.conversation_id)
    previous_component_class = component_class[component_type]

    if previous_component_class:
        builder = component_map[previous_component_class]
        return previous_component_class, builder(chat_args)
    else:
        random_component_class = random_component_by_score(component_type, component_map)
        print(f"random_component_class: {random_component_class}")
        builder = component_map[random_component_class]
        return random_component_class, builder(chat_args)


def build_chat(chat_args: ChatArgs):
    """
    :param chat_args: ChatArgs object containing
        conversation_id, pdf_id, metadata, and streaming flag.

    :return: A chain

    Example Usage:

        chain = build_chat(chat_args)
    """
    retriever_name, retriever = select_component("retriever", retriever_map, chat_args)
    llm_name, llm = select_component("llm", llm_map, chat_args)
    memory_name, memory = select_component("memory", memory_map, chat_args)
    print(f"running chain with memory: {memory_name}, llm: {llm_name}, retriever: {retriever_name}")
    set_conversation_components(
        conversation_id=chat_args.conversation_id, 
        llm=llm_name, 
        retriever=retriever_name, 
        memory=memory_name
        )

    condense_question_llm = ChatOpenAI(streaming=False)
   
    
    return StreamingConversationalRetrievalChain.from_llm(
        llm=llm,
        condense_question_llm=condense_question_llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        verbose=True
    )

    
