from typing import Iterator

import openai
import pandas as pd
import streamlit as st
import tiktoken
from dotenv import load_dotenv
from st_aggrid import AgGrid, GridOptionsBuilder


@st.cache_data
def load_dotenv_():
    load_dotenv()


load_dotenv_()

# Make the layout wider
st.set_page_config(layout="wide")


class PDFReader:
    @st.cache_data
    def read(_self, file_path: str) -> str:
        try:
            import PyPDF2

            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                return " ".join(page.extract_text() for page in reader.pages)
        except Exception as e:
            raise DocumentReaderError(f"Error reading PDF: {str(e)}")


class OpenAIProcessor:
    def __init__(self):
        self.client = openai.OpenAI()
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))

    def count_message_tokens(self, messages: list[dict]) -> int:
        """
        Count tokens in a message list according to OpenAI's token counting logic
        https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
        """
        num_tokens = 0
        for message in messages:
            # Every message follows {role: ..., content: ...} format
            num_tokens += (
                4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            )
            for key, value in message.items():
                num_tokens += len(self.encoding.encode(str(value)))
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens

    def process_query(self, query: str, context: str) -> Iterator[str]:
        try:
            # Calculate tokens for each component
            system_tokens = self.count_tokens(
                "You are a helpful assistant answering questions about wedding venues based on their descriptions."
            )
            context_tokens = self.count_tokens(context)
            query_tokens = self.count_tokens(query)

            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant answering questions about wedding venues based on their descriptions.",
                },
                {
                    "role": "user",
                    "content": f"Context about the venues:\n{context}\n\nQuestion: {query}",
                },
            ]

            total_tokens = self.count_message_tokens(messages)

            print("\n=== Token Usage Details ===")
            print(f"System message: {system_tokens} tokens")
            print(f"Context: {context_tokens} tokens")
            print(f"Query: {query_tokens} tokens")
            print(f"Total tokens (including message formatting): {total_tokens}")
            print("========================\n")

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                stream=True,
            )

            response_tokens = 0
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content.replace("$", r"\$")
                    response_tokens += self.count_tokens(content)
                    yield content

            print("\n=== Final Token Count ===")
            print(f"Response tokens: {response_tokens}")
            print(f"Total tokens used: {total_tokens + response_tokens}")
            print("======================\n")

        except Exception as e:
            raise ProcessorError(f"Error processing query: {str(e)}")


class DocumentReaderError(Exception):
    pass


class ProcessorError(Exception):
    pass


def main():
    # Initialize chat history and PDF processor in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "processor" not in st.session_state:
        st.session_state.processor = OpenAIProcessor()
    if "pdf_reader" not in st.session_state:
        st.session_state.pdf_reader = PDFReader()

    st.title("Wedding Venue Explorer")

    # Load your data
    df = pd.read_csv("venue_info_test copy 2.csv")
    # Reorder columns to put venue_name first
    cols = df.columns.tolist()
    cols.remove("venue_name")
    df = df[["venue_name"] + cols]

    # Configure grid options
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection(selection_mode="multiple", use_checkbox=True)
    gb.configure_column("file", hide=True)
    gb.configure_column("venue_name", headerName="Venue Name")
    # Enable advanced filtering
    gb.configure_default_column(
        filterable=True, enableRowGroup=True, enableValue=True, enablePivot=True
    )
    grid_options = gb.build()

    # Display the interactive grid
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        width="100%",
        enable_enterprise_modules=True,
    )

    # Get selected rows
    selected_df = pd.DataFrame(grid_response["selected_rows"])

    if len(selected_df) == 0:
        st.warning("Please select one or more venues.")

    chat_container = st.container()

    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if prompt := st.chat_input("Ask about the selected wedding venue(s)"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Create context about selected venues
        venue_context = "No wedding venue(s) selected"
        if (selected_df is not None) and (not selected_df.empty):
            venue_texts = []
            for _, row in selected_df.iterrows():
                try:
                    pdf_text = st.session_state.pdf_reader.read(row["file"])
                    venue_texts.append(f"Venue: {row['venue_name']}\n{pdf_text}")
                except DocumentReaderError as e:
                    st.error(f"Error reading PDF for {row['venue_name']}: {str(e)}")
                    continue

            if venue_texts:
                venue_context = "\n\n".join(venue_texts)

        try:
            # Stream the response
            response = st.chat_message("assistant").write_stream(
                st.session_state.processor.process_query(prompt, venue_context)
            )

            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
        except ProcessorError as e:
            st.error(f"Error processing request: {str(e)}")

        # Rerun to display the new messages
        st.rerun()


if __name__ == "__main__":
    main()
