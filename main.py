# from app.graph import LLMNodeGraph

# llm_graph = LLMNodeGraph()
# graph = llm_graph.chatbot()
# llm_graph.show_graph()

from app.anime import LLMNodeGraph

llm_graph = LLMNodeGraph()
graph = llm_graph.builder_node()


def stream_graph_updates(user_input: str):
    for event in graph.stream(
        { "input": user_input} ,
        stream_mode="messages"     
        ):
        if event[0].content != 'vue':
            print(event[0].content, end="", flush=True)
    print('\n\n')

while True:
    try:
        
        user_input = input("User(quit、exit、q): ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except Exception as e:
        print(e)
        print("Exit goodbye!")
        break