"use client"

import { useState, useEffect } from "react"

// Global styles
// const GlobalStyle = createGlobalStyle`
//   @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');

//   body {
//     margin: 0;
//     padding: 0;
//     background-color: #111;
//     font-family: 'Orbitron', sans-serif;
//   }
// `

// Styled components
// const AppContainer = styled.div`
//   background-color: #111;
//   color: #e0e0e0;
//   min-height: 100vh;
//   padding: 40px;
// `

// const Title = styled.h1`
//   color: #0ff;
//   text-align: center;
//   font-size: 3rem;
//   margin-bottom: 2rem;
//   text-shadow: 0 0 10px #0ff;
// `

// const InputContainer = styled.div`
//   margin-bottom: 1.5rem;
// `

// const Label = styled.label`
//   display: block;
//   margin-bottom: 0.5rem;
//   color: #0f0;
// `

// const TextArea = styled.textarea`
//   width: 100%;
//   padding: 0.5rem;
//   background-color: #222;
//   border: 1px solid #0f0;
//   color: #0f0;
//   font-family: 'Courier New', monospace;
//   resize: vertical;
// `

// const Input = styled.input`
//   width: 100%;
//   padding: 0.5rem;
//   background-color: #222;
//   border: 1px solid #0f0;
//   color: #0f0;
//   font-family: 'Courier New', monospace;
// `

// const Button = styled.button`
//   background-color: #0f0;
//   color: #000;
//   border: none;
//   padding: 0.75rem 1.5rem;
//   font-size: 1rem;
//   cursor: pointer;
//   transition: all 0.3s ease;
//   font-family: 'Orbitron', sans-serif;

//   &:hover {
//     background-color: #0ff;
//     box-shadow: 0 0 10px #0ff;
//   }

//   &:disabled {
//     background-color: #444;
//     cursor: not-allowed;
//   }
// `

// const UpdatesContainer = styled.div`
//   margin-top: 2rem;
// `

// const UpdatesList = styled.ul`
//   list-style-type: none;
//   padding: 0;
// `

// const fadeIn = keyframes`
//   from { opacity: 0; transform: translateY(20px); }
//   to { opacity: 1; transform: translateY(0); }
// `

// const UpdateItem = styled.li`
//   margin-bottom: 0.5rem;
//   padding: 0.5rem;
//   background-color: #222;
//   border-left: 3px solid #0f0;
//   animation: ${fadeIn} 0.5s ease-out;
// `

// const AudioContainer = styled.div`
//   margin-top: 2rem;
//   text-align: center;
// `

// const AudioPlayer = styled.audio`
//   width: 100%;
//   margin-top: 1rem;
// `

// Icons (simplified version without using lucide-react)
// const MusicIcon = () => (
//   <span role="img" aria-label="music" style={{ fontSize: "1.5em", marginRight: "0.5em" }}>
//     🎵
//   </span>
// )

// const ZapIcon = () => (
//   <span role="img" aria-label="zap" style={{ fontSize: "1.2em", marginLeft: "0.5em" }}>
//     ⚡
//   </span>
// )

const App = () => {
  const [musicianInput, setMusicianInput] = useState("")
  const [style, setStyle] = useState("Romantic era")
  const [updates, setUpdates] = useState([])
  const [audioUrl, setAudioUrl] = useState("")
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    // Add Orbitron font
    const link = document.createElement("link")
    link.href = "https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap"
    link.rel = "stylesheet"
    document.head.appendChild(link)

    // Add global styles
    const style = document.createElement("style")
    style.textContent = `
      body {
        margin: 0;
        padding: 0;
        background-color: #111;
        font-family: 'Orbitron', sans-serif;
        color: #e0e0e0;
      }
      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
      }
    `
    document.head.appendChild(style)

    return () => {
      document.head.removeChild(link)
      document.head.removeChild(style)
    }
  }, [])

  const handleCompose = () => {
    setUpdates([])
    setAudioUrl("")
    setLoading(true)

    const eventSource = new EventSource(
      `http://localhost:5000/compose_steps?musician_input=${encodeURIComponent(musicianInput)}&style=${encodeURIComponent(style)}`,
    )
    eventSource.onmessage = (e) => {
      const data = JSON.parse(e.data)
      if (data.line) {
        setUpdates((prev) => [...prev, data.line])
      }
      if (data.final) {
        fetch("http://localhost:5000/compose", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ musician_input: musicianInput, style }),
        })
          .then((res) => res.json())
          .then((data) => {
            if (data.success) {
              setAudioUrl(data.wav_url)
            } else {
              setUpdates((prev) => [...prev, "Error: " + data.error])
            }
            setLoading(false)
            eventSource.close()
          })
          .catch((err) => {
            console.error("Error calling /compose:", err)
            setUpdates((prev) => [...prev, "Error during final generation."])
            setLoading(false)
            eventSource.close()
          })
      }
    }
    eventSource.onerror = (err) => {
      console.error("EventSource error:", err)
      setLoading(false)
      eventSource.close()
    }
  }

  const styles = {
    appContainer: {
      backgroundColor: "#111",
      minHeight: "100vh",
      padding: "40px",
    },
    title: {
      color: "#0ff",
      textAlign: "center",
      fontSize: "3rem",
      marginBottom: "2rem",
      textShadow: "0 0 10px #0ff",
    },
    inputContainer: {
      marginBottom: "1.5rem",
    },
    label: {
      display: "block",
      marginBottom: "0.5rem",
      color: "#0f0",
    },
    textArea: {
      width: "100%",
      padding: "0.5rem",
      backgroundColor: "#222",
      border: "1px solid #0f0",
      color: "#0f0",
      fontFamily: "Courier New, monospace",
      resize: "vertical",
    },
    input: {
      width: "100%",
      padding: "0.5rem",
      backgroundColor: "#222",
      border: "1px solid #0f0",
      color: "#0f0",
      fontFamily: "Courier New, monospace",
    },
    button: {
      backgroundColor: "#0f0",
      color: "#000",
      border: "none",
      padding: "0.75rem 1.5rem",
      fontSize: "1rem",
      cursor: "pointer",
      transition: "all 0.3s ease",
      fontFamily: "Orbitron, sans-serif",
    },
    updatesContainer: {
      marginTop: "2rem",
    },
    updatesList: {
      listStyleType: "none",
      padding: 0,
    },
    updateItem: {
      marginBottom: "0.5rem",
      padding: "0.5rem",
      backgroundColor: "#222",
      borderLeft: "3px solid #0f0",
      animation: "fadeIn 0.5s ease-out",
    },
    audioContainer: {
      marginTop: "2rem",
      textAlign: "center",
    },
    audioPlayer: {
      width: "100%",
      marginTop: "1rem",
    },
  }

  return (
    <div style={styles.appContainer}>
      <h1 style={styles.title}>
        <span role="img" aria-label="music" style={{ fontSize: "0.8em", marginRight: "0.5em" }}>
          🎵
        </span>
         Music Compositor
        <span role="img" aria-label="music" style={{ fontSize: "0.8em", marginLeft: "0.5em" }}>
          🎵
        </span>
      </h1>
      <div style={styles.inputContainer}>
        <label style={styles.label}>
          Enter your musical idea:
          <textarea
            style={styles.textArea}
            value={musicianInput}
            onChange={(e) => setMusicianInput(e.target.value)}
            rows={4}
          />
        </label>
      </div>
      <div style={styles.inputContainer}>
        <label style={styles.label}>
          Style:
          <input style={styles.input} type="text" value={style} onChange={(e) => setStyle(e.target.value)} />
        </label>
      </div>
      <button
        style={{ ...styles.button, ...(loading ? { backgroundColor: "#444", cursor: "not-allowed" } : {}) }}
        onClick={handleCompose}
        disabled={loading}
      >
        {loading ? "Generating..." : "Generate Music"}
        <span role="img" aria-label="zap" style={{ fontSize: "1.2em", marginLeft: "0.5em" }}>
          ⚡
        </span>
      </button>
      <div style={styles.updatesContainer}>
        <h2>Composition Progress</h2>
        <ul style={styles.updatesList}>
          {updates.map((line, idx) => (
            <li key={idx} style={styles.updateItem}>
              {line}
            </li>
          ))}
        </ul>
      </div>
      {audioUrl && (
        <div style={styles.audioContainer}>
          <h2>Your Generated Music</h2>
          <audio style={styles.audioPlayer} controls src={audioUrl}>
            Your browser does not support the audio element.
          </audio>
        </div>
      )}
    </div>
  )
}

export default App

