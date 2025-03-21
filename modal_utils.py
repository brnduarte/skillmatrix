import streamlit as st

def create_modal(title, key="modal", initial_state=False):
    """
    Create a modal dialog.
    
    Args:
        title: Title of the modal
        key: Unique key for the modal
        initial_state: Initial state (open/closed)
        
    Returns:
        Boolean indicating if the modal is open
    """
    # Initialize session state for this modal if it doesn't exist
    if f"modal_{key}" not in st.session_state:
        st.session_state[f"modal_{key}"] = initial_state
    
    return st.session_state[f"modal_{key}"]

def open_modal(key="modal"):
    """Open a modal dialog"""
    st.session_state[f"modal_{key}"] = True

def close_modal(key="modal"):
    """Close a modal dialog"""
    st.session_state[f"modal_{key}"] = False

def render_modal(title, content_function, key="modal", width=700):
    """
    Render a modal dialog with the given content.
    
    Args:
        title: Title of the modal
        content_function: Function that renders the content of the modal
        key: Unique key for the modal
        width: Width of the modal in pixels
    """
    is_open = st.session_state.get(f"modal_{key}", False)
    
    if is_open:
        # Create a container for the modal background (overlay)
        modal_overlay = st.container()
        
        # Set up the modal container
        with modal_overlay:
            # Apply CSS for the modal overlay
            st.markdown(
                f"""
                <div class="modal-backdrop" style="
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0, 0, 0, 0.5);
                    z-index: 1000;
                "></div>
                
                <div class="modal-container" style="
                    position: fixed;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    width: {width}px;
                    max-width: 95%;
                    max-height: 90vh;
                    overflow-y: auto;
                    background-color: white;
                    border-radius: 5px;
                    z-index: 1001;
                    padding: 20px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                ">
                    <div class="modal-header" style="
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        border-bottom: 1px solid #e0e0e0;
                        padding-bottom: 10px;
                        margin-bottom: 15px;
                    ">
                        <h3 style="margin: 0;">{title}</h3>
                        <button onclick="window.streamlitCloseModal_{key}()" style="
                            background: none;
                            border: none;
                            font-size: 20px;
                            cursor: pointer;
                        ">×</button>
                    </div>
                    <div id="modal-content-{key}"></div>
                </div>
                
                <script>
                    window.streamlitCloseModal_{key} = function() {{
                        const elems = window.parent.document.querySelectorAll('button[kind=secondaryFormSubmit]');
                        for (const el of elems) {{
                            if (el.innerText === 'Close {key}') {{
                                el.click();
                            }}
                        }}
                    }};
                </script>
                """,
                unsafe_allow_html=True
            )
            
            # Add a hidden button that can be clicked via JavaScript
            if st.button(f"Close {key}", key=f"close_{key}", type="secondary"):
                close_modal(key)
                st.rerun()
            
            # Create a container for the modal content
            content_container = st.container()
            
            # Render the content
            with content_container:
                content_function()

def display_as_table(df, columns_to_display=None, actions=None, id_column="id", key_prefix="table"):
    """
    Display a dataframe as a table with action buttons.
    
    Args:
        df: DataFrame to display
        columns_to_display: List of columns to display (if None, display all columns)
        actions: Dictionary of action functions, e.g., {'Edit': edit_function, 'Delete': delete_function}
        id_column: Column containing the ID value to pass to the action functions
        key_prefix: Prefix for button keys
    """
    if df.empty:
        st.info("No data available.")
        return
    
    # If no columns specified, use all columns except ID
    if columns_to_display is None:
        columns_to_display = [col for col in df.columns if col != id_column]
    
    # Create a table header
    cols = st.columns([3] * len(columns_to_display) + [1] * len(actions or []))
    
    # Display column headers
    for i, col_name in enumerate(columns_to_display):
        with cols[i]:
            st.markdown(f"**{col_name}**")
    
    # Display action headers
    if actions:
        for i, action_name in enumerate(actions.keys()):
            with cols[len(columns_to_display) + i]:
                st.markdown(f"**{action_name}**")
    
    # Display rows
    for _, row in df.iterrows():
        row_cols = st.columns([3] * len(columns_to_display) + [1] * len(actions or []))
        
        # Display row data
        for i, col_name in enumerate(columns_to_display):
            with row_cols[i]:
                st.write(row[col_name])
        
        # Display action buttons
        if actions:
            for i, (action_name, action_fn) in enumerate(actions.items()):
                with row_cols[len(columns_to_display) + i]:
                    if st.button(
                        action_name, 
                        key=f"{key_prefix}_{action_name}_{row[id_column]}", 
                        type="secondary",
                        use_container_width=True
                    ):
                        action_fn(row[id_column])