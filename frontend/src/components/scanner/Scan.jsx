import { useState, useRef, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { FiImage } from 'react-icons/fi'
import api from '../../services/api'
import './Scan.css'

const Scan = () => {
    const { id } = useParams()
    const [processing, setProcessing] = useState(false)
    const [webcamActive, setWebcamActive] = useState(false)
    const fileInputRef = useRef(null)
    const videoRef = useRef(null)
    const canvasRef = useRef(null)
    const streamRef = useRef(null)
    const navigate = useNavigate()

    const isMobile = () => /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)

    useEffect(() => {
        if (!isMobile()) {
            startWebcam()
        }
        return () => {
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop())
            }
        }
    }, [])

    const startWebcam = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: { facingMode: { ideal: 'environment' } } 
            })
            streamRef.current = stream
            if (videoRef.current) {
                videoRef.current.srcObject = stream
            }
            setWebcamActive(true)
        } catch (error) {
            console.error('Erro ao acessar câmera:', error)
            alert('Não foi possível acessar a câmera. Use a opção de galeria para selecionar uma imagem.')
        }
    }

    const stopWebcam = () => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop())
            streamRef.current = null
        }
        if (videoRef.current) {
            videoRef.current.srcObject = null
        }
        setWebcamActive(false)
    }

    const capturePhoto = async () => {
        if (!videoRef.current || !canvasRef.current) return
        
        const video = videoRef.current
        const canvas = canvasRef.current
        
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        const ctx = canvas.getContext('2d')
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
        
        canvas.toBlob(async (blob) => {
            if (blob) {
                const file = new File([blob], 'capture.jpg', { type: 'image/jpeg' })
                await processarImagem(file)
            }
        }, 'image/jpeg', 0.9)
    }

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
        stopWebcam();
        navigate(`/feira/${id}`, { replace: true });
    };

    return (
        <div className="scanner-container">
            <header className="scanner-header">
                <h1>OCR de etiquetas</h1>
            </header>

            {processing && (
                <div className="scanner-loading">
                    <div className="spinner"></div>
                    <p>Processando imagem...</p>
                </div>
            )}

            <div className="scanner-capture-area">
                {webcamActive ? (
                    <video
                        ref={videoRef}
                        autoPlay
                        playsInline
                        style={{
                            width: '90%',
                            maxWidth: '320px',
                            height: '200px',
                            objectFit: 'cover',
                            borderRadius: '12px',
                            border: '2px solid var(--primary-color)'
                        }}
                    />
                ) : (
                    <div className="capture-frame" />
                )}
                <p className="instruction-text">Posicione a etiqueta dentro da área</p>
            </div>

            <div className="scanner-actions">
                {!isMobile() && (
                    <button className="gallery-button" onClick={handleGallerySelect} aria-label="Selecionar imagem" disabled={processing}>
                        <FiImage />
                    </button>
                )}

                {webcamActive ? (
                    <button className="capture-button" onClick={capturePhoto} disabled={processing} />
                ) : isMobile() ? (
                    <button className="capture-button" onClick={handleGallerySelect} disabled={processing} />
                ) : (
                    <button className="capture-button" onClick={startWebcam} disabled={processing} />
                )}

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
            
            <canvas ref={canvasRef} style={{ display: 'none' }} />
        </div>
    )
}

export default Scan