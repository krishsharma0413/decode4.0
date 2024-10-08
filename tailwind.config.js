/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/*.html", "./templates/components/*.html"],
  theme: {
    extend: {
      colors:{
        "background": "#181818",
        "text": "#F2F2F2",
        "primary": "#DEDEDE",
        "links": "#606060",
        "easy-bg": "#868686",
        "medium-bg": "#585858",
        "hard-bg": "#2F2F2F",   
      },
      fontFamily:{
        "nulshock": "Nulshock",
        "dos": "dos",
        "poppins": "Poppins",
      }
    },
  },
  plugins: [],
}

