from composio import ComposioToolSet, App
toolset = ComposioToolSet()
for app in [App.PDF_API_IO, App.PDF_CO, App.API2PDF]:
    print(f"=== {app.name} ===")
    try:
        actions = toolset.get_actions(app=app)
        for action in actions:
            print(f"- {action.name}")
    except Exception as e:
        print(f"Error: {e}")
