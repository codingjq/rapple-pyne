
import pynecone as pc
from rapple.styles import app_style, guess_box_style, lyric_style, drop_list_style

import datetime
import random
import json


class InputGuess(pc.State):

    song_title: str
    song_artist: str
    song_lyrics: list

    all_songs: list = None
    song_of_the_day: dict
    song_fetched: bool = False

    guess_index: int = 0
    guess_color: str = "none"
    guesses: dict = {}
    guess_boxes: dict = {0:"⬜", 1:"⬜", 2:"⬜", 3:"⬜", 4:"⬜"}
    current_guess: str|None = ""
    current_guess_id: str
    
    performances : list[dict]= [
        {"title":"Aced it!", "description": "You know your bars!"}, 
        {"title":"Great Job!", "description": "You're a Hip-Hop head"}, 
        {"title": "Pretty Good", "description": "You know your stuff"}, 
        {"title":"Fair", "description": "Okay, okay, hopefully you do better tomorrow!"}, 
        {"title":"Whew that was close!", "description": "Come on! Do better tomorrow!"}, 
        {"title" :"Try Again Tomorrow!", "description": "You didn't get it. Oh well."}
        ]
    end_game_screen = False

    
    selectable_songs: list[dict] = []

    box_colors: list = ["none" for i in range(0,5)]
    buttons_disabled: bool = False
 
    @pc.var
    def visible_lyrics(self) -> list:
        offset = 0
        if self.guess_index < 5:
            offset = 1
        bars = []
        if self.song_fetched == True:
            lyrics = json.loads(self.song_of_the_day["lyrics"])
            lyric_num=0
            lyric_counter=0
            while lyric_num < self.guess_index+offset:
                lyric = lyrics[lyric_counter]
                if "[" in lyric:
                    pass
                else:
                    bars.append(lyric)
                    lyric_num+=1
                lyric_counter+=1
            for i in range(self.guess_index+1,5):
                bars.append("-")
            
        return bars


    def handle_current_guess(self, e):
        print(e)
        self.current_guess = e
        print(self.current_guess)

        if self.all_songs == None:
            with pc.session() as session:
                self.all_songs = list(map(lambda r: r.dict(), session.query(SongModel).all()))

        title_list = list(filter(lambda songs:self.current_guess.lower() in songs["title"].lower(), self.all_songs))
        artist_list = list(filter(lambda songs:self.current_guess.lower() in songs["artist"].lower(), self.all_songs))
        full_list = [*title_list, *artist_list]
        self.selectable_songs = []
        for item in full_list[0:8]:
            self.selectable_songs.append({"id": item["id"], "title": item["title"], "artist": item["artist"]})
        self.selectable_songs = self.selectable_songs

    @pc.var
    def suggested_guess(self) -> list:
        suggested=[]
        for item in self.selectable_songs:
            if len(self.selectable_songs) > 0:
                suggested.append((item["title"] + "- " + item["artist"])[0:29])
        return suggested
    
    def handle_from_list(self, song):
        self.current_guess = f'{song["title"]}- {song["artist"]}'
        self.selectable_songs = []
        self.current_guess_id = song["id"]

    def clear_selectables(self):
        if len(self.selectable_songs) > 0:
            self.selectable_songs = []

    @pc.var
    def box_color(self) -> list:
        if str in self.box_colors:
            return self.box_colors

    def end_game(self):
        self.end_game_screen = True
        self.buttons_disabled = True
        with pc.session() as session:
            session.add(
                Performance(
                    guess_index=self.guess_index,
                    date=datetime.date.today().strftime(f"%d-%m-%y")
                )
            )
            session.commit()

    @pc.var
    def get_performance(self) -> dict:
        return self.performances[self.guess_index]

    @pc.var
    def get_player_boxes(self) -> str:
        my_string = "#Rapple "
        today_str = datetime.date.today().strftime(f"%d-%m-%y")
        for i in range(0, len(self.guess_boxes)):
            my_string += self.guess_boxes[i]
        else:
            my_string += " "
            my_string += today_str
            my_string += " "
            my_string += "https://rapple.lol"
        return my_string

    def copy_clipboard(self):
        '''I think I have to wrap a react-clipboard-copier'''
        pass
    
    def submit_guess(self):
        if self.current_guess == "":
            return
        if self.guess_index<5:
            self.guesses[self.guess_index] = self.current_guess
            if str(self.current_guess_id) == str(self.song_of_the_day["song_id"]):
                self.box_colors[self.guess_index] = "green"
                self.guess_boxes[self.guess_index] = "🟩"
                return self.end_game()
            else:
                self.box_colors[self.guess_index] = "darkred"
                self.guess_boxes[self.guess_index] = "🟥"
            self.box_colors = self.box_colors
            self.guess_index += 1
            self.guesses = self.guesses
            self.current_guess = ""
        if self.guess_index == 5:
            return self.end_game()
        

    def skip(self):
        if self.guess_index<5:
            self.guesses[self.guess_index] = "Skipped"
            self.guess_boxes[self.guess_index] = "⬛"
            self.guess_index += 1
            self.guesses = self.guesses
            self.current_guess = ""
        if self.guess_index == 5:
            return self.end_game()

class QuestionModal(InputGuess):
    show: bool = True

    def change(self):
        self.show = not (self.show)

class InfoModal(InputGuess):
    show: bool = False

    def change(self):
        self.show = not (self.show)

class Performance(pc.Model, table=True):
    guess_index: int
    date: str

class SongModel(pc.Model, table=True):
    artist: str
    title: str
    lyrics: str

class DailySong(pc.Model, table=True):
    artist: str
    title: str
    lyrics: str
    date: str
    song_id: str

class GetDailySong(InputGuess):

    def get_song(self):
        if self.song_fetched == True:
            return
        today_str = datetime.date.today().strftime(f"%d-%m-%y")
        with pc.session() as session:
            today_song = session.query(DailySong).filter(DailySong.date.contains(today_str)).all()
            if len(today_song) > 0:
                self.song_of_the_day = today_song[0].dict()
                self.song_fetched = True
            else:
                all_songs = list(map(lambda r: r.dict(), session.query(SongModel).all()))
                
                def no_repeat():
                    today_song = random.choice(all_songs)
                    t_id = today_song["id"]
                    all_dailies = list(map(lambda r: r.dict(), session.query(DailySong).all()))
                    if len(list(filter(lambda song: song["song_id"]==t_id, all_dailies)))>0 :
                        no_repeat()
                    else:
                        return today_song

                today_song = no_repeat()    
                t_artist = today_song["artist"]
                t_title = today_song["title"]
                t_lyrics = today_song["lyrics"]
                t_id = today_song["id"]
                t_date = today_str
                

                session.add(
                    DailySong(
                        artist=t_artist, title=t_title, lyrics=t_lyrics, date=t_date, song_id=t_id
                )
                    )
                session.commit()
                return GetDailySong.get_song
                


def song_lyrics_item(lyric):
    return pc.list_item(lyric, style=lyric_style)

def selectable_songs_item(song):
    return pc.list_item(song["title"] + "- " + song["artist"], style=drop_list_style, on_click=lambda _: InputGuess.handle_from_list(song))

def index() -> pc.Component:
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
                                                        " love of Rap and inspiration",
                                                        " from other daily guesser genre games. It is built entirely in Python using ",
                                                        pc.link("@Pynecone-io.", href="https://pynecone.io", is_external=True, color="coral"), 
                                                        " You can support ",
                                                         pc.link("@CodingJQ", href="https://youtube.com/@codingjq", is_external=True, color="coral"),
                                                         " by watching and subscribing to his YouTube channel."), 
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
                                                        pc.icon(tag="StarIcon"), pc.text("You start with one lyric and start guessing.")
                                                ),
                                                    pc.hstack(
                                                        pc.icon(tag="StarIcon"), pc.text("Each missed answer reveals another song lyric."),
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
                            spacing="5rem",
                                ),
                            ),
                    width="100%",
                    border_bottom="1px solid darkgrey",
                    margin_top="1rem",
                    padding_bottom="1rem",
                    ),
                
                pc.cond(
                    InputGuess.end_game_screen,
                    pc.vstack(
                        pc.heading("Today's Banger", padding_bottom="4rem"),
                        pc.image(),
                        pc.text(InputGuess.song_of_the_day["title"]),
                        pc.text("by"),
                        pc.text(InputGuess.song_of_the_day["artist"], padding_bottom="4rem"),
                        pc.text(InputGuess.get_player_boxes),
                        pc.heading(InputGuess.get_performance["title"], padding_top="4rem"),
                        pc.text(InputGuess.get_performance["description"], padding_bottom="4rem"),
                          pc.hstack(pc.text("Check out my YouTube channel"), pc.link("CodingJQ", href="https://youtube.com/@codingjq", is_external=True, color="coral")),
                          pc.hstack(pc.text("Learn about "), pc.link("Pynecone", href="https://pynecone.io", color="coral")),
                    ),
                      
                    
                    pc.vstack(
                pc.center(
                    pc.vstack(
                        pc.box(InputGuess.guesses[0], bg=InputGuess.box_colors[0],style=guess_box_style),
                        pc.box(InputGuess.guesses[1], bg=InputGuess.box_colors[1], style=guess_box_style),
                        pc.box(InputGuess.guesses[2], bg=InputGuess.box_colors[2], style=guess_box_style),
                        pc.box(InputGuess.guesses[3], bg=InputGuess.box_colors[3], style=guess_box_style),
                        pc.box(InputGuess.guesses[4], bg=InputGuess.box_colors[4], style=guess_box_style),
                        pc.text("Lyrics", align_text="center"),
                    )
                ),
                pc.vstack(
                    
                    pc.cond(
                        InputGuess.song_fetched,
                        pc.list(
                        pc.foreach(
                            InputGuess.visible_lyrics,
                            song_lyrics_item,
                        ),
                    ),
                        pc.circular_progress(is_indeterminate=True)
                    ),
                    
                ),   
                pc.hstack(
                    pc.container(
                        pc.input(defaultValue=InputGuess.current_guess, on_change=InputGuess.handle_current_guess,placeholder="Guess Title of Song",  on_click=InputGuess.clear_selectables, border="1px solid darkgrey"),
                        pc.list(
                        pc.foreach(
                            InputGuess.selectable_songs,
                            selectable_songs_item,
                            ),
                    position="absolute",
                    ),
                        width="40rem", z_index=10, max_width="80vw"
                    ),
                    pc.icon(tag="SearchIcon")
                    , 
                  
                ),
                pc.hstack(
                    pc.button("Skip", bg="grey", width="8rem", height="3rem", on_click=InputGuess.skip, is_disabled=InputGuess.buttons_disabled ),
                    pc.button("Guess", color="darkgreen", bg="lightgreen", width="8rem", height="3rem", on_click=InputGuess.submit_guess, is_disabled=InputGuess.buttons_disabled),
                ),
                ),
    ),
                font_size="1em",

            )


def result():
    return pc.vstack(
        pc.text("Results")
    )


# Add state and page to the app.
app = pc.App(state=InputGuess, style=app_style)
app.add_page(index, on_load=GetDailySong.get_song, title="Rapple", description="Hip Hop daily guesser by @codingjq")
app.add_page(result)
app.compile()
