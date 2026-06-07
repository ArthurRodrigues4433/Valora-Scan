import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FiImage } from 'react-icons/fi'
import './Scan.css'

const Scan = () => {
    const [capturing, setCapturing] = useState(false)
    const navigate = useNavigate()

    const handleCapture = () => {
        setCapturing(true)
        // TODO: Implement OCR capture logic
    }

    const handleGallerySelect = () => {
        // TODO: Implement gallery selection logic
    }

    const handleCancel = () => {
        navigate('/home')
    }

    return (
        <div className="scanner-container">
            <header className="scanner-header">
                <h1>OCR de etiquetas</h1>
            </header>

            <div className="scanner-capture-area">
                <div className="capture-frame" />
                <p className="instruction-text">Posicione a etiqueta dentro da área</p>
            </div>

            <div className="scanner-actions">
                <button className="gallery-button" onClick={handleGallerySelect} aria-label="Selecionar imagem">
                    <FiImage />
                </button>

                <button className="capture-button" onClick={handleCapture} disabled={capturing} />

                <button className="cancel-button" onClick={handleCancel}>
                    Cancelar
                </button>
            </div>
        </div>
    )
}

export default Scan