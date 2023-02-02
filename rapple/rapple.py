
from pcconfig import config
import pynecone as pc
from rapple.styles import app_style, guess_box_style, lyric_style, drop_list_style

import json 
import datetime


class InputGuess(pc.State):

    song_title: str
    song_artist: str
    song_lyrics: list

    all_songs: list = None


    guess_index: int = 0
    guess_color: str = "none"
    guesses: dict = {}
    current_guess: str|None = None
    
    selectable_songs= []
    selectable_ids: list = []
    selectable_titles: list = []
    selectable_artist: list = []


    box_colors = ["none" for i in range(0,5)]


    def handle_current_guess(self, e):
        self.current_guess = e
        if self.all_songs == None:
            self.get_all_songs()

        title_list = list(filter(lambda songs:self.current_guess.lower() in songs["title"].lower(), self.all_songs))
        artist_list = list(filter(lambda songs:self.current_guess.lower() in songs["artist"].lower(), self.all_songs))
        full_list = [*title_list, *artist_list]
        self.selectable_songs = []
        for item in full_list[0:8]:
            self.selectable_songs.append({"id": item["id"], "title": item["title"], "artist": item["artist"]})
        self.selectable_songs = self.selectable_songs
        # print(self.selectable_songs)

    @pc.var
    def suggested_guess(self) -> list:
        suggested=[]
        for item in self.selectable_songs:
            if len(self.selectable_songs) > 0:
                suggested.append((item["title"] + "- " + item["artist"])[0:29])
        return suggested
    
    def handle_from_list(self, song_id):
        self.current_guess = song_id
        self.selectable_songs = []
        print(song_id)

    def clear_selectables(self):
        if len(self.selectable_songs) > 0:
            self.selectable_songs = []


    @pc.var
    def display_guesses(self):
        
        for guess in self.guesses:
            pass
        pass

    def toggle_color(self) -> str:
        if self.guess_color == "none":
            self.guess_color = "yellow"
        else:
            self.guess_color = "none"

    @pc.var
    def box_color(self) -> list:
        if str in self.box_colors:
            return self.box_colors


    def submit_guess(self):
        if self.guess_index<5:
            self.guesses[self.guess_index] = self.current_guess
            self.box_colors[self.guess_index] = "darkred"
            self.box_colors = self.box_colors
            self.guess_index += 1
            self.guesses = self.guesses
            self.current_guess = ""
        

    def skip(self):
        print("fire")


    def get_song_of_day(self):
        today_str = datetime.date.today().strftime(f"%d-%m-%y")
        with pc.session() as session:
            song = (
                session.query(SongOfTheDay)
                .filter(SongOfTheDay.date.contains(today_str))
                .all()
            )
        self.song_artist = song["artist"]
        self.song_title = song["title"]
        self.song_lyrics = song["lyrics"][1:6]

    @pc.var
    def get_all_songs(self):
        with pc.session() as session:
            self.all_songs = list(map(lambda r: r.dict(), session.query(SongModel).all()))

class QuestionModal(InputGuess):
    show: bool = False

    def change(self):
        self.show = not (self.show)

class InfoModal(InputGuess):
    show: bool = False

    def change(self):
        self.show = not (self.show)

class SongModel(pc.Model, table=True):
    artist: str
    title: str
    lyrics: str

class QuerySongModel(InputGuess):
    
    def add_songs(self):
        with open("scraping/new_output.json") as f:
            my_json = json.load(f)
        for song in my_json:
            with pc.session() as session:
                session.add(
                    SongModel(
                        artist = song["artist"],
                        title = song["title"],
                        lyrics = json.dumps(song["lyrics"])
                    )
                )
                session.commit()

    


class SongOfTheDay(pc.Model):
    artist: str
    title: str
    lyrics: str
    date: str


class GetSongOfTheDay(InputGuess):
    
    def get_song(self):
        today_str = datetime.date.today().strftime(f"%d-%m-%y")
        with pc.session() as session:
            self.song = (
                session.query(SongOfTheDay)
                .filter(SongOfTheDay.date.contains(today_str))
                .all()
            )
        
        if self.song != None:
            return self.song
        all_songs = QuerySongModel().get_all_songs()
        print(all_songs)


def selectable_songs_item(song):
    print(song)
    return pc.list_item(song, style=drop_list_style, on_click=lambda _: InputGuess.handle_from_list(song))


def index():
    return  pc.vstack(
                pc.box(
                    pc.center(
                        pc.hstack(
                            pc.icon(tag="InfoOutlineIcon", on_click=InfoModal.change, _hover={"cursor": "pointer"}),
                                pc.modal(
                                    pc.modal_overlay(
                                        pc.modal_content(
                                            pc.modal_header("About Rapple"),
                                            pc.modal_body(
                                                pc.vstack(
                                                    pc.center(
                                                        pc.text("Rapple was made with ",
                                                        pc.link("@CodingJQ's", href="https://youtube.com/@codingjq", is_external=True, color="coral"),
                                                        "love of Rap and inspiration",
                                                        "from other daily guesser genre games. It is built entirely in Python using the ",
                                                        pc.link("@Pynecone-io.", href="https://pynecone.io", is_external=True, color="coral"), 
                                                        "You can support",
                                                         pc.link("@CodingJQ", href="https://youtube.com/@codingjq", is_external=True, color="coral"),
                                                         "by watching and subscribing to his YouTube channel."), 
                                                ),
                                            ),
                                        ),
                                                pc.modal_footer(
                                                    pc.button(
                                                        "Thanks", on_click=InfoModal.change, bg="lightgreen", color="darkgreen"
                                                    ),
                                                ),
                                                style=app_style,  border="1px solid darkgrey"
                                    ),
                                ), is_open=InfoModal.show,
                                
                                ), 
                            pc.heading("Rapple", font_size="2rem", user_select="none"),
                            pc.box(
                                pc.icon(tag="QuestionOutlineIcon", on_click=QuestionModal.change, _hover={"cursor": "pointer"}),
                                pc.modal(
                                    pc.modal_overlay(
                                        pc.modal_content(
                                            pc.modal_header("How to play Rapple"),
                                            pc.modal_body(
                                                pc.vstack(
                                                    pc.hstack(
                                                        pc.icon(tag="StarIcon"), pc.text("Daily song will reset at 00:01 UTC")
                                                    ),
                                                    pc.hstack(
                                                        pc.icon(tag="StarIcon"), pc.text("Read the bars, then guess the song and artist.")
                                                ),
                                                    pc.hstack(
                                                        pc.icon(tag="StarIcon"), pc.text("Skips and incorrect guesses reveal a new bar."),
                                                    ),
                                                    pc.hstack(
                                                        pc.icon(tag="StarIcon"), pc.text("Get it right in the fewest tries and share!")
                                                    )
                                            ),
                                        ),
                                                pc.modal_footer(
                                                    pc.button(
                                                        "Let's Go", on_click=QuestionModal.change, bg="lightgreen", color="darkgreen"
                                                    ),
                                                ),
                                                style=app_style,  border="1px solid darkgrey"
                                    ),
                                ), is_open=QuestionModal.show,
                                
                                ),   
                            ),
                            spacing="10rem"
                                ),
                            ),
                    width="100%",
                    border_bottom="1px solid darkgrey",
                    margin_top="1rem",
                    padding_bottom="1rem",
                    ),
                pc.center(
                    pc.vstack(
                        pc.box(InputGuess.guesses[0], bg=InputGuess.box_colors[0],style=guess_box_style),
                        pc.box(InputGuess.guesses[1], bg=InputGuess.box_colors[1], style=guess_box_style),
                        pc.box(InputGuess.guesses[2], bg=InputGuess.box_colors[2], style=guess_box_style),
                        pc.box(InputGuess.guesses[3], bg=InputGuess.box_colors[3], style=guess_box_style),
                        pc.box(InputGuess.guesses[4], bg=InputGuess.box_colors[4], style=guess_box_style),
                    )
                ),
                pc.vstack(
                    pc.box(InputGuess.song_lyrics[0]),
                    pc.box("My mind flies, wide eyes, I cry", style=lyric_style),
                    pc.box("For the people that, for the people that, for the people that, for the people", style=lyric_style),
                    pc.box("For the people that, for the people that, for the people that, for the people", style=lyric_style),
                    pc.box("_", style=lyric_style),
                ),   
                pc.hstack(
                    pc.container(
                        pc.input(value=InputGuess.current_guess, placeholder="Guess Title of Song", on_change=InputGuess.handle_current_guess, on_click=InputGuess.clear_selectables, border="1px solid darkgrey"),
                        pc.list(
                        pc.foreach(
                            InputGuess.suggested_guess,
                            selectable_songs_item,
                            ),
                    position="absolute",
                    ),
                        width="50rem", z_index=10
                    ),
                    pc.icon(tag="SearchIcon"),
                  
                ),
                pc.hstack(
                    pc.button("Skip", bg="grey", width="8rem", height="3rem", on_click=InputGuess.skip),
                    pc.button("Guess", color="darkgreen", bg="lightgreen", width="8rem", height="3rem", on_click=InputGuess.submit_guess),
                ),
                
                font_size="1em",

            )


def result():
    return pc.vstack(
        pc.text("Results")
    )


# Add state and page to the app.
app = pc.App(state=InputGuess, style=app_style)
app.add_page(index)
app.add_page(result)
app.compile()
