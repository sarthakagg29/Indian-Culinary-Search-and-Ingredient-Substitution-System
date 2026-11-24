# Deployment: GitHub, then Streamlit Community Cloud

Free, takes about 15 minutes. Button names on the websites change now and then, so match by meaning.

## 0. Check the folder
The folder you push must contain `app.py`, all `page_*.py` files, `ui_common.py`, `backend.py`, `requirements.txt`, the `D2_*.py` and `D3_*.py` files, every `.csv` and the three `Ahn_input_*.tsv` files, all at the top level (not inside another folder).

## 1. Run it on your own computer first
```
python -m venv .venv
.venv\Scripts\activate          # Windows      (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```
A browser tab opens at `http://localhost:8501`. Search `ghee`; you should see butter, coconut oil and other oils under **Known swaps**. The first search takes a second or two while the flavour data loads. Stop with Ctrl+C.

## 2. Put it on GitHub
1. Make a free account at github.com. Install Git from git-scm.com if you do not have it.
2. On GitHub click **New repository**. Name it e.g. `cgas-ingredient-app`. Choose **Private**, because the repo holds a GPL-3.0 data copy (see the licence check below). Streamlit Community Cloud can deploy private repos once you give it access. Do **not** tick "Add a README" (you already have one). Click **Create repository**.
3. In a terminal, inside your project folder:
```
git init
git add .
git commit -m "CGAS Streamlit app, Deliverable 4"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/cgas-ingredient-app.git
git push -u origin main
```
4. When asked to log in, use the browser sign-in window, or a Personal Access Token as the password (GitHub, Settings, Developer settings, Personal access tokens). GitHub Desktop is an easier alternative if the terminal is a hassle: File, Add local repository, Publish.
5. Refresh the repo page. You should see all the files. `.gitignore` already keeps `__pycache__` out.

**Licence check before ever making it public:** the `Ahn_input_*.tsv` files are a copy of data released under GPL-3.0 (see README.md). If you are unsure, make the repository **Private**: Streamlit Community Cloud can deploy private repos once you allow it access.

**Teammate access:** repo, Settings, Collaborators, Add people.

## 3. Deploy on Streamlit Community Cloud
1. Go to **share.streamlit.io** and sign in with GitHub. Allow access to your repositories when asked.
2. Click **Create app** (or **New app**), then choose to deploy from an existing GitHub repo.
3. Fill in:
   - Repository: `YOUR-USERNAME/cgas-ingredient-app`
   - Branch: `main`
   - Main file path: `app.py`
   - App URL: pick a name, e.g. `cgas-ingredients` (gives `https://cgas-ingredients.streamlit.app`)
4. Open **Advanced settings** and choose Python **3.12** (3.10 to 3.13 are all fine; avoid the newest release if plotly or pandas has no build for it yet).
5. Click **Deploy**. The first build takes a couple of minutes while it installs from `requirements.txt`. Then the app opens at your URL.

## 4. Updating later
Change the code, then `git add .`, `git commit -m "what changed"`, `git push`. Streamlit Cloud redeploys on its own within a minute.

## 5. If something goes wrong
| What you see | Likely cause and fix |
|---|---|
| `ModuleNotFoundError: D2_5_search` | The D2 files are not at the top level of the repo, or a name has different capitals. Linux is case-sensitive. |
| `ModuleNotFoundError: plotly` | `requirements.txt` is missing or not at the top level. |
| `FileNotFoundError: ...csv` or `...tsv` | A data file did not get pushed. Compare the file list on GitHub with your folder. |
| Hindi shows as boxes or `???` | Rare. Make sure files were saved as UTF-8 and not converted. |
| "This app has gone to sleep" | Free apps sleep after inactivity. Click the wake button; it starts in about 30 seconds. Open the link once before a demo. |
| Build fails | Open **Manage app** (bottom right of the app), read the log, fix, push again. |
