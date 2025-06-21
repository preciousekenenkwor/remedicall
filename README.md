<img width="959" alt="image" src="https://github.com/user-attachments/assets/ee229a9e-6203-4395-ad12-3241dbdd5066" />

## To Run Frontend locally

```bash
cd frontend
npm install
npm start
```
## To run backend locally

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux

pip install -r requirements.txt
uvicorn main:app --reload
```
