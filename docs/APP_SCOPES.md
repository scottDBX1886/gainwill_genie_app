# App user authorization scopes (Genie)

The app needs **user authorization** and these scopes so it can call Genie and run SQL on your behalf:

- **dashboards.genie** – use Genie (conversations, query results)
- **sql** – run SQL (e.g. Genie-generated queries)

They are set in the bundle (`resources/gainwell_genie_app.app.yml` → `user_api_scopes`) and applied when you run `databricks bundle deploy -t dev`.

## Where to see scopes in the UI

1. In the workspace, go to **Apps** in the sidebar.
2. Open your app (e.g. **gainwell-genie-app-dev**).
3. Use **Settings** (gear) or **Edit** for the app.
4. Open the **Configure** (or **Authorization**) step.
5. Under **User authorization**, you should see the list of scopes (e.g. **dashboards.genie**, **sql**).  
   If you don’t see **User authorization** or **+ Add scope**, a workspace admin may need to enable user authorization for apps first.

## If you still get “does not have required scopes”

- Close the app tab and open the app again from **Apps** so a new token (with the new scopes) is issued.
- If your org requires it, ask a workspace admin to grant consent for the app so users get the scopes without a prompt.
