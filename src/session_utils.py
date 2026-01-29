import streamlit as st
import streamlit.components.v1 as components

def keep_alive():
    """
    Injects a hidden JavaScript ping to keep the Streamlit websocket connection alive.
    This helps prevent the app from going into 'sleep' or disconnecting due to inactivity.
    """
    keep_alive_html = """
    <script>
    var lastPing = new Date().getTime();
    setInterval(function() {
        var now = new Date().getTime();
        // Ping every 30 seconds
        if (now - lastPing > 30000) {
            console.log("Keep-alive ping");
            fetch(window.location.href); 
            lastPing = now;
        }
    }, 5000); // Check every 5 seconds
    </script>
    """
    components.html(keep_alive_html, height=0, width=0)
