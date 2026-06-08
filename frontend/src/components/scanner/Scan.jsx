import { useState, useRef } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { FiImage } from 'react-icons/fi'
import api from '../../services/api'
import './Scan.css'

const Scan = () => {
    const { id } = useParams()
    const [capturing, setCapturing] = useState(false)
    const [processing, setProcessing] = useState(false)
    const fileInputRef = useRef(null)
    const navigate = useNavigate()

    const processarImagem = async (file) => {
        if (!file) return
        
        setProcessing(true)
        try {
            const formData = new FormData()
            formData.append('file', file)
            
            const response = await api.post('/ocr/etiqueta', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })
            
            const previewUrl = URL.createObjectURL(file)
            
            navigate(`/feira/${id}/confirmar`, {
                state: {
                    produto: response.data.produto,
                    ocrTexto: response.data.texto_extrato,
                    confianca: response.data.confianca,
                    previewUrl: previewUrl,
                    imagemUrl: null
                }
            })
        } catch (error) {
            console.error('Erro ao processar imagem:', error)
            alert('Erro ao escanear etiqueta')
        } finally {
            setProcessing(false)
        }
    }

    const handleCapture = () => {
        setCapturing(true)
        fileInputRef.current?.click()
    }

    const handleGallerySelect = () => {
        fileInputRef.current?.click()
    }

    const handleFileChange = async (e) => {
        const file = e.target.files?.[0]
        if (file) {
            await processarImagem(file)
        }
        e.target.value = ''
    }

    const handleCancel = () => {
        navigate(`/feira/${id}`)
    }

    return (
        <div className="scanner-container">
            <header className="scanner-header">
                <h1>OCR de etiquetas</h1>
            </header>

            {(processing || capturing) && (
                <div className="scanner-loading">
                    <div className="spinner"></div>
                    <p>Processando imagem...</p>
                </div>
            )}

            <div className="scanner-capture-area">
                <div className="capture-frame" />
                <p className="instruction-text">Posicione a etiqueta dentro da área</p>
            </div>

            <div className="scanner-actions">
                <button className="gallery-button" onClick={handleGallerySelect} aria-label="Selecionar imagem" disabled={processing}>
                    <FiImage />
                </button>

                <button className="capture-button" onClick={handleCapture} disabled={processing} />

                <button className="cancel-button" onClick={handleCancel} disabled={processing}>
                    Cancelar
                </button>
            </div>

            <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                capture="environment"
                onChange={handleFileChange}
                style={{ display: 'none' }}
            />
        </div>
    )
}

export default Scan