import streamlit as st
import PyPDF2
import io
import requests
import json

def main():
    st.set_page_config(page_title="AI Resume Critiquer", page_icon=":)", layout="centered")
    st.title("AI Resume Critiquer")
    st.markdown("Upload your resume in PDF format and get feedback on how to improve it.")
    
    # Ollama configuration
    ollama_url = st.text_input("Ollama URL", value="http://localhost:11434", help="URL where Ollama is running")
    
    # Get available models and let user select
    if st.button("🔄 Refresh Models"):
        st.rerun()
    
    models = get_available_models(ollama_url)
    if models:
        st.success(f"✅ Connected to Ollama! Found {len(models)} models")
        model_name = st.selectbox("Select Model", models, help="Choose from your installed models")
        
        # Show model details
        for model in models:
            if model == model_name:
                model_info = get_model_info(ollama_url, model)
                if model_info:
                    st.info(f"📊 Model: {model} | Size: {model_info.get('size', 'Unknown')} | Modified: {model_info.get('modified_at', 'Unknown')}")
    else:
        st.error("❌ No models found. Please install a model first:")
        st.code("ollama pull llama3.2")
        st.code("ollama pull mistral")
        model_name = st.text_input("Or enter model name manually:", value="llama3.2")
    
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf", "txt"])
    job_role = st.text_input("Enter the job role you are targeting (optional)")
    
    # Add an Analyze button
    analyze = st.button("🔍 Analyze Resume")
    
    # Debug: Add breakpoint option
    if st.checkbox("🐛 Enable Debug Mode"):
        st.write("**Debug Info:**")
        st.write(f"- Ollama URL: {ollama_url}")
        st.write(f"- Selected Model: {model_name}")
        st.write(f"- Available Models: {models}")
        st.write(f"- File uploaded: {uploaded_file.name if uploaded_file else 'None'}")
        st.write(f"- Job role: {job_role or 'Not specified'}")
        
        # Add option to test connection
        if st.button("🔧 Test Model Connection"):
            test_response = query_ollama(ollama_url, model_name, "Hello! Just testing the connection.")
            if test_response:
                st.success("✅ Model connection test successful!")
            else:
                st.error("❌ Model connection test failed!")
    
    if analyze and uploaded_file:
        try:
            print(f"🚀 DEBUG: Starting resume analysis")
            print(f"🚀 DEBUG: Ollama URL: {ollama_url}")
            print(f"🚀 DEBUG: Selected model: {model_name}")
            print(f"🚀 DEBUG: Available models: {models}")
            
            # Test if model exists before processing
            if not models or model_name not in models:
                print(f"❌ DEBUG: Model '{model_name}' not found in available models")
                st.error(f"Model '{model_name}' not found. Available models: {', '.join(models) if models else 'None'}")
                st.info("Install a model with: `ollama pull llama3.2` or `ollama pull mistral`")
                st.stop()
            
            print(f"📁 DEBUG: Extracting text from file: {uploaded_file.name}")
            file_content = extract_text_from_file(uploaded_file)
            
            if not file_content.strip():
                print(f"❌ DEBUG: File content is empty")
                st.error("The uploaded file is empty or could not be read.")
                st.stop()
            
            print(f"📝 DEBUG: Extracted {len(file_content)} characters from file")
            print(f"📝 DEBUG: First 200 chars: {file_content[:200]}...")
            
            # Create prompt for resume analysis  
            job_context = f"The user is applying for the following job role: {job_role}" if job_role else "No specific job role mentioned."
            
            prompt = f"""You are an expert resume reviewer and career counselor. Please analyze the following resume and provide detailed, actionable feedback.

{job_context}

Resume Content:
{file_content}

Please provide feedback in the following areas:
1. Overall Structure and Format
2. Content Quality and Relevance
3. Skills and Experience Presentation
4. Areas for Improvement
5. Specific Recommendations

Be constructive and specific in your feedback."""

            print(f"🤖 DEBUG: Sending prompt to Ollama (length: {len(prompt)} chars)")
            
            # Show loading spinner
            with st.spinner("Analyzing your resume..."):
                response = query_ollama(ollama_url, model_name, prompt)
            
            if response:
                print(f"✅ DEBUG: Got response from Ollama (length: {len(response)} chars)")
                st.markdown("### 📋 Resume Analysis & Feedback:")
                st.markdown(response)
            else:
                print(f"❌ DEBUG: No response from Ollama")
                st.error("Failed to get response from Ollama. Please try again.")

        except Exception as e:
            print(f"💥 DEBUG: Exception occurred: {e}")
            import traceback
            print(f"💥 DEBUG: Full traceback:\n{traceback.format_exc()}")
            st.error(f"Error: {e}")

def test_ollama_connection(ollama_url):
    """Test if Ollama is running and accessible"""
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_available_models(ollama_url):
    """Get list of available models from Ollama"""
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = []
            for model in data.get('models', []):
                # Get the model name, handle different formats
                name = model.get('name', '')
                if ':' in name:
                    models.append(name)  # Keep full name with tag
                else:
                    models.append(name)
            return sorted(models)
        else:
            st.error(f"Failed to get models: HTTP {response.status_code}")
    except Exception as e:
        st.error(f"Error connecting to Ollama: {e}")
    return []

def get_model_info(ollama_url, model_name):
    """Get detailed info about a specific model"""
    try:
        payload = {"name": model_name}
        response = requests.post(f"{ollama_url}/api/show", json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'size': format_bytes(data.get('size', 0)),
                'modified_at': data.get('modified_at', '').split('T')[0] if data.get('modified_at') else 'Unknown',
                'family': data.get('details', {}).get('family', 'Unknown')
            }
    except:
        pass
    return None

def format_bytes(bytes_value):
    """Convert bytes to human readable format"""
    if bytes_value == 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"

def query_ollama(ollama_url, model_name, prompt):
    """Send request to Ollama and get response"""
    try:
        # Debug info
        st.info(f"🔍 Debug: Using model '{model_name}' at {ollama_url}")
        
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 2000
            }
        }
        
        # Debug: Show payload (without full prompt)
        debug_payload = payload.copy()
        debug_payload['prompt'] = f"{prompt[:100]}..." if len(prompt) > 100 else prompt
        st.code(f"Debug Payload: {json.dumps(debug_payload, indent=2)}")
        
        response = requests.post(
            f"{ollama_url}/api/generate",
            json=payload,
            timeout=180
        )
        
        # Debug: Show response details
        st.info(f"🔍 Debug: Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            st.success("✅ Got successful response from Ollama!")
            return result.get('response', 'No response field found')
        else:
            st.error(f"❌ Ollama API error: {response.status_code}")
            st.error(f"Response text: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        st.error("Request timed out. The model might be taking too long to respond.")
        return None
    except Exception as e:
        st.error(f"Error querying Ollama: {e}")
        return None

def extract_text_from_file(uploaded_file):
    """Extract text from uploaded file (PDF or TXT)"""
    try:
        print(f"📁 DEBUG: Processing file: {uploaded_file.name}")
        print(f"📁 DEBUG: File type: {uploaded_file.type}")
        print(f"📁 DEBUG: File size: {uploaded_file.size} bytes")
        print(f"📁 DEBUG: File object type: {type(uploaded_file)}")
        print(f"📁 DEBUG: File object dir: {dir(uploaded_file)}")
        
        # Check if uploaded_file is None or invalid
        if uploaded_file is None:
            print("❌ DEBUG: uploaded_file is None")
            st.error("No file provided")
            return ""
        
        # Try different methods to get the file content
        file_bytes = None
        
        # Method 1: Try getvalue() if it's a BytesIO-like object
        if hasattr(uploaded_file, 'getvalue'):
            try:
                file_bytes = uploaded_file.getvalue()
                print(f"📁 DEBUG: Got bytes using getvalue(): {len(file_bytes)} bytes, type: {type(file_bytes)}")
            except Exception as e:
                print(f"📁 DEBUG: getvalue() failed: {e}")
        
        # Method 2: Try read() method
        if file_bytes is None:
            try:
                uploaded_file.seek(0)  # Ensure we're at the beginning
                file_bytes = uploaded_file.read()
                print(f"📁 DEBUG: Got bytes using read(): {len(file_bytes)} bytes, type: {type(file_bytes)}")
                uploaded_file.seek(0)  # Reset pointer
            except Exception as e:
                print(f"📁 DEBUG: read() failed: {e}")
                st.error(f"Could not read file: {e}")
                return ""
        
        # Verify we have valid data
        if file_bytes is None or len(file_bytes) == 0:
            print("❌ DEBUG: No file content retrieved")
            st.error("File appears to be empty or could not be read")
            return ""
        
        # Process PDF files
        if uploaded_file.type == "application/pdf" or uploaded_file.name.lower().endswith('.pdf'):
            print("📄 DEBUG: Processing as PDF")
            
            # Ensure we have bytes for PyPDF2
            if not isinstance(file_bytes, bytes):
                print(f"📄 DEBUG: Converting {type(file_bytes)} to bytes")
                try:
                    if hasattr(file_bytes, 'encode'):
                        file_bytes = file_bytes.encode('utf-8')
                    else:
                        file_bytes = bytes(file_bytes)
                except Exception as convert_error:
                    print(f"❌ DEBUG: Failed to convert to bytes: {convert_error}")
                    st.error("Could not convert file content to bytes")
                    return ""
            
            # Create BytesIO object from the bytes
            try:
                pdf_buffer = io.BytesIO(file_bytes)
                pdf_buffer.seek(0)  # Ensure we're at the start
                print(f"📄 DEBUG: Created BytesIO buffer with {len(file_bytes)} bytes")
            except Exception as buffer_error:
                print(f"❌ DEBUG: Failed to create BytesIO: {buffer_error}")
                st.error("Could not create PDF buffer")
                return ""
            
            # Create PDF reader from BytesIO
            try:
                pdf_reader = PyPDF2.PdfReader(pdf_buffer)
                print(f"📄 DEBUG: Successfully created PdfReader with {len(pdf_reader.pages)} pages")
            except Exception as pdf_error:
                print(f"❌ DEBUG: PyPDF2.PdfReader failed: {pdf_error}")
                st.error(f"Could not read PDF file: {pdf_error}")
                return ""
            
            # Extract text from all pages
            text = ""
            for i, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                        print(f"📄 DEBUG: Page {i+1} extracted {len(page_text)} characters")
                    else:
                        print(f"📄 DEBUG: Page {i+1} - no text extracted")
                except Exception as page_error:
                    print(f"📄 DEBUG: Error extracting page {i+1}: {page_error}")
                    continue
            
            print(f"📄 DEBUG: Total extracted text: {len(text)} characters")
            return text.strip()
            
        else:
            # Handle as text file
            print("📄 DEBUG: Processing as text file")
            
            if isinstance(file_bytes, bytes):
                try:
                    text = file_bytes.decode("utf-8")
                    print(f"📄 DEBUG: Successfully decoded as UTF-8")
                except UnicodeDecodeError as decode_error:
                    print(f"📄 DEBUG: UTF-8 decode failed: {decode_error}")
                    # Try different encodings
                    for encoding in ['latin1', 'cp1252', 'iso-8859-1']:
                        try:
                            text = file_bytes.decode(encoding)
                            print(f"📄 DEBUG: Successfully decoded with {encoding}")
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        text = file_bytes.decode('utf-8', errors='ignore')
                        print("📄 DEBUG: Decoded with error handling (some chars may be lost)")
            else:
                text = str(file_bytes)
                print(f"📄 DEBUG: Converted to string directly")
            
            print(f"📄 DEBUG: Text file content length: {len(text)} characters")
            return text.strip()
            
    except Exception as e:
        print(f"❌ DEBUG: Unexpected error in extract_text_from_file: {e}")
        print(f"❌ DEBUG: Error type: {type(e)}")
        import traceback
        traceback.print_exc()  # This will print to console for VS Code debugging
        st.error(f"Error reading file: {e}")
        return ""

if __name__ == "__main__":
    main()