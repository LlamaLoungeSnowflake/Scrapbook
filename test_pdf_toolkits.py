import os
import json
import base64
from dotenv import load_dotenv
from composio import ComposioToolSet, App, Action

load_dotenv()

def test_toolkits():
    if not os.environ.get("COMPOSIO_API_KEY"):
        print("❌ Error: COMPOSIO_API_KEY not found in environment.")
        print("Please add 'COMPOSIO_API_KEY=your_key_here' to your .env file.")
        return

    print("Initialize Composio toolset...")
    toolset = ComposioToolSet()
    
    html_path = "assets/resume.html"
    if not os.path.exists(html_path):
        print(f"❌ Error: {html_path} not found.")
        return

    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    apps_to_test = [App.PDF_API_IO, App.PDF_CO, App.API2PDF]
    
    for app in apps_to_test:
        print(f"\n" + "="*40)
        print(f"🚀 Testing {app.name}")
        print("="*40)
        try:
            actions = toolset.get_actions(app=app)
            html_to_pdf_action = None
            
            # Find the action matching html and pdf
            for action in actions:
                name = action.name.lower()
                if "html" in name and "pdf" in name:
                    html_to_pdf_action = action
                    break
            
            if not html_to_pdf_action:
                print(f"⚠️ Could not find an HTML to PDF action for {app.name}.")
                print(f"Available actions: {[a.name for a in actions]}")
                continue
                
            print(f"✅ Found action: {html_to_pdf_action.name}")
            
            # Show parameters
            schema = html_to_pdf_action.parameters
            print("\n📝 Expected Parameters Schema:")
            print(json.dumps(schema, indent=2))
            
            # Try to build payload dynamically based on schema properties
            params = {}
            if schema and 'properties' in schema:
                props = schema['properties']
                # Common payload keys
                for key in ['html', 'htmlCode', 'source', 'html_content', 'content']:
                    if key in props:
                        params[key] = html_content
                        # Add a dummy name if required
                        if 'name' in props:
                            params['name'] = f"test_{app.name.lower()}.pdf"
                        if 'fileName' in props:
                            params['fileName'] = f"test_{app.name.lower()}.pdf"
                        break
                
                # If API2PDF specific
                if app == App.API2PDF and 'html' in props:
                    params['html'] = html_content
                
                # Let's see if we successfully mapped
                if not params:
                    print(f"⚠️ Warning: Could not automatically map parameters. Keys found: {list(props.keys())}")
                    # We will try a fallback with 'html' anyway
                    params['html'] = html_content
            else:
                params['html'] = html_content

            print(f"\n⚙️ Executing {html_to_pdf_action.name}...")
            
            response = toolset.execute_action(
                action=html_to_pdf_action, 
                params=params
            )
            
            print(f"\n✅ Result from {app.name}:")
            print(json.dumps(response, indent=2))
            
            # If the response contains a url or base64 data, we can optionally save or print it
            # e.g., pdf.co returns {"url": "..."} usually
            # api2pdf returns {"FileUrl": "..."}

        except Exception as e:
            print(f"❌ Failed to test {app.name}: {e}")

if __name__ == "__main__":
    test_toolkits()
