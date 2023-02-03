import pynecone as pc

app_style = {
    "background": "var(--chakra-colors-gray-800)",
    "color": "var(--chakra-colors-white)",
    "font_family": "tahoma",
}

guess_box_style = {
    "bg": "none",
    "text_align":"center", 
    "padding_top": "5px",
    "border":"1px solid darkgrey",
    "width":"40rem", "height":"2.5rem", 
    "border_radius":"5"
}

lyric_style = {
    "user_select": "none",
    "color": "white",
    "text-align": "center",
}

drop_list_style = {
    "user_select": "none",
    "width": "20rem",
    "height": "2rem",
    "bg": "var(--chakra-colors-gray-800)",
    "border": "1px solid darkgrey",
    "border_radius": "transparent",
    "_hover": { "color":"coral", "cursor": "pointer", "transform":"scale(105%)"},
    "_active": {"color":"lightgreen"},
    "padding_left": "1rem"
}
