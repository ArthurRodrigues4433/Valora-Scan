import { useState, useRef, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { FiImage } from 'react-icons/fi'
import api from '../../services/api'
import './Scan.css'

const Scan = () => {
    const { id } = useParams()
    const navigate = useNavigate()
    const [processing, setProcessing] = useState(false)
    const [webcamActive, setWebcamActive] = useState(false)
    const [cameraSupported, setCameraSupported] = useState(true)
    const fileInputRef = useRef(null)
    const videoRef = useRef(null)
    const canvasRef = useRef(null)
    const streamRef = useRef(null)

    useEffect(() => {
        startWebcam()

        return () => {
            stopWebcam()
        }
    }, [])

    const startWebcam = async () => {
        if (streamRef.current) return

        if (!navigator.mediaDevices?.getUserMedia) {
            setCameraSupported(false)
            return
        }

        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: {
                        ideal: 'environment'
                    }
                }
            })

            streamRef.current = stream

            if (videoRef.current) {
                videoRef.current.srcObject = stream
            }

            setWebcamActive(true)
            setCameraSupported(true)

        } catch (error) {
            console.error(error)

            setWebcamActive(false)
            setCameraSupported(false)
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

    const capturePhoto = () => {
        if (!videoRef.current || !canvasRef.current) return

        const video = videoRef.current

        if (video.videoWidth === 0) {
            return
        }

        const canvas = canvasRef.current

        canvas.width = video.videoWidth
        canvas.height = video.videoHeight

        const ctx = canvas.getContext('2d')

        ctx.drawImage(video, 0, 0)

        canvas.toBlob(async blob => {
            if (!blob) return

            const file = new File(
                [blob],
                'capture.jpg',
                {
                    type: 'image/jpeg'
                }
            )

            await processarImagem(file)

        }, 'image/jpeg', 0.9)
    }

    const processarImagem = async (file) => {
        if (!file) return

        setProcessing(true)

        try {

            const formData = new FormData()

            formData.append('file', file)

            const response = await api.post(
                '/ocr/etiqueta',
                formData,
                {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                }
            )

            stopWebcam()

            const previewUrl = URL.createObjectURL(file)

            navigate(`/feira/${id}/confirmar`, {
                state: {
                    produto: response.data.produto,
                    ocrTexto: response.data.texto_extrato,
                    confianca: response.data.confianca,
                    previewUrl,
                    imagemUrl: null
                }
            })

        } catch (error) {

            console.error(error)

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
        stopWebcam()
        navigate(`/feira/${id}`, {
            replace: true
        })
    }

    return (
        <div className="scanner-container">

            <header className="scanner-header">
                <h1>OCR de Etiquetas</h1>
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

                <p className="instruction-text">
                    Posicione a etiqueta dentro da área
                </p>

            </div>

            <div className="scanner-actions">

                <button
                    className="gallery-button"
                    onClick={handleGallerySelect}
                    disabled={processing}
                >
                    <FiImage />
                </button>

                {webcamActive && (

                    <button
                        className="capture-button"
                        onClick={capturePhoto}
                        disabled={processing}
                    />

                )}

                {!webcamActive && cameraSupported && (

                    <button
                        className="capture-button"
                        onClick={startWebcam}
                        disabled={processing}
                    />

                )}

                <button
                    className="cancel-button"
                    onClick={handleCancel}
                    disabled={processing}
                >
                    Cancelar
                </button>

            </div>

            <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                capture="environment"
                onChange={handleFileChange}
                style={{
                    display: 'none'
                }}
            />

            <canvas
                ref={canvasRef}
                style={{
                    display: 'none'
                }}
            />

        </div>
    )
}

export default Scan