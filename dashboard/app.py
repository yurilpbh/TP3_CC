import pandas as pd, os, json, datetime

from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


class Song(BaseModel):
    songs: list


app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Get recommended songs"}


@app.post("/get_recommendation")
def get_recommendation(data: Song):
    songs = data.songs
    filename = '/dataset/csv_model.csv'
    if os.path.isfile(filename):
        file_date = os.path.getctime(filename)
        file_date = datetime.date.fromtimestamp(file_date)
    version_file = '/dataset/model_version.json'
    version = 0
    with open(version_file, 'r') as file:
        json_version = json.load(file)
        version = json_version['version']
    df = pd.read_csv(filename)
    songs_recommendation = []
    df_recommendation = pd.DataFrame()
    songs_choosed = []
    for song in songs:
        song = song.lower()
        df_songs = df[df['antecedents'].str.lower() == song]
        df_recommendation = pd.concat([df_recommendation, df_songs])
        songs_recommendation.append(df_songs['consequents'].tolist())
        songs_choosed.append(song)
    
    # Use set intersection to find common elements
    common_elements = set(songs_recommendation[0])
    for sublist in songs_recommendation[1:]:
        common_elements &= set(sublist)
        
    for song in common_elements:
        songs_choosed.append(song.lower())
        
    if len(common_elements) < 5:
        df = df[~df['consequents'].str.lower().isin(songs_choosed)]
        common_elements.update(df.sort_values('consequent support', ascending=False)['consequents'].drop_duplicates()[0:(5-len(common_elements))].to_list())

        return {
                "songs": common_elements,
                "version": version,
                "model_date": file_date,
            }
    else:
        return {
            "songs": list(common_elements)[0:5],
            "version": version,
            "model_date": file_date,
        }


if __name__ == '__main__':
    app.run(debug=True)
