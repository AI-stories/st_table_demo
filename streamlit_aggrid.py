import os
import tempfile
from typing import Iterator, List, Union, overload

import openai
import pandas as pd
import streamlit as st
import tiktoken
from dotenv import load_dotenv
from st_aggrid import AgGrid, GridOptionsBuilder

from wedding_venues import download_files

# This must be the first st command
st.set_page_config(layout="wide")


@st.cache_data
def load_dotenv_():
    load_dotenv()


load_dotenv_()


class MarkdownReader:
    @staticmethod
    def _get_temp_dir() -> str:
        """Get or create a temporary directory that persists for the session"""
        if "temp_dir" not in st.session_state:
            st.session_state.temp_dir = tempfile.mkdtemp()
            print(f"Created temporary directory: {st.session_state.temp_dir}")
        return st.session_state.temp_dir

    @staticmethod
    @overload
    def download(file_path: str) -> str:
        """Download a single markdown file and return the target path"""
        ...

    @staticmethod
    @overload
    def download(file_paths: List[str]) -> List[str]:
        """Download multiple markdown files and return the target paths"""
        ...

    @staticmethod
    def download(file_paths: Union[str, List[str]]) -> Union[str, List[str]]:
        """
        Download markdown files to a temporary directory

        Args:
            file_paths: Single file path (str) or list of file paths (list[str])

        Returns:
            If input is str: Returns target path (str)
            If input is list[str]: Returns list of target paths (list[str])
        """
        temp_dir = MarkdownReader._get_temp_dir()

        if isinstance(file_paths, str):
            source_file = file_paths
            target_file = os.path.join(temp_dir, os.path.basename(source_file))
            download_files([source_file], [target_file])
            return target_file

        else:
            source_files = file_paths
            target_files = [
                os.path.join(temp_dir, os.path.basename(f)) for f in source_files
            ]
            download_files(source_files, target_files)
            return target_files

    @staticmethod
    @st.cache_data
    def read(file_path: str) -> str:
        """Read content from a file path"""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            raise DocumentReaderError(f"Error reading file {file_path}: {str(e)}")


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
    # Initialize chat history and processor in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "processor" not in st.session_state:
        st.session_state.processor = OpenAIProcessor()
    if "markdown_reader" not in st.session_state:
        st.session_state.markdown_reader = MarkdownReader()

    st.title("Wedding Venue Explorer")

    # Load your data
    df = pd.read_csv("venue_info_test.csv")
    # Reorder columns to put venue_name first
    cols = df.columns.tolist()
    if "venue_name" in cols:
        cols.remove("venue_name")
        df = df[["venue_name"] + cols]

    # Configure grid options
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection(selection_mode="multiple", use_checkbox=True)
    # Only hide file column if it exists
    if "file" in df.columns:
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
            # Construct file paths from venue names
            venue_names = selected_df["venue_name"].tolist()
            source_files = [f"venue_md/{venue_name}.md" for venue_name in venue_names]

            try:
                # Bulk download all files
                target_files = MarkdownReader.download(source_files)

                # Create a mapping from venue names to downloaded files
                file_mapping = dict(zip(venue_names, target_files))

                # Read all downloaded files
                venue_texts = []
                for _, row in selected_df.iterrows():
                    venue_name = row["venue_name"]
                    try:
                        venue_text = MarkdownReader.read(file_mapping[venue_name])
                        venue_texts.append(f"Venue: {venue_name}\n{venue_text}")
                    except DocumentReaderError as e:
                        st.error(f"Error reading markdown for {venue_name}: {str(e)}")
                        continue
                    except KeyError:
                        st.error(f"Could not find markdown file for {venue_name}")
                        continue
            except Exception as e:
                st.error(f"Error bulk downloading files: {str(e)}")
                venue_texts = []

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
