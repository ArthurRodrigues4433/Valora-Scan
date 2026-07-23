import { useState, useEffect, useRef } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { IoArrowBack, IoQrCode } from 'react-icons/io5'
import jsQR from 'jsqr'
import api from '../../services/api'
import './ScanNFCe.css'

const ScanNFCe = () => {
    const { id } = useParams()
    const navigate = useNavigate()
    const [processing, setProcessing] = useState(false)
    const [webcamActive, setWebcamActive] = useState(false)
    const [cameraSupported, setCameraSupported] = useState(true)
    const [chaveManual, setChaveManual] = useState('')
    const [error, setError] = useState('')
    const [scanning, setScanning] = useState(false)
    const videoRef = useRef(null)
    const canvasRef = useRef(null)
    const streamRef = useRef(null)
    const animationFrameRef = useRef(null)

    const [routerError, setRouterError] = useState(null)
    const [dadosNota, setDadosNota] = useState(null)
    const [comparacao, setComparacao] = useState(null)

    const validarFeira = async () => {
        try {
            const response = await api.get(`/feiras/feira/${id}`)
            const feira = response.data

            if (feira.status === 'finalizada') {
                alert('Esta feira já foi finalizada.')
                navigate('/feiras', { replace: true })
                return false
            }

            if (!feira.itens || feira.itens.length === 0) {
                alert('Adicione pelo menos um produto à feira antes de escanear a nota fiscal.')
                navigate(`/feira/${id}`, { replace: true })
                return false
            }

            return true
        } catch (error) {
            console.error(error)
            if (error.response?.status === 404) {
                alert('Feira não encontrada.')
            } else if (error.response?.status === 403) {
                alert('Você não possui acesso a esta feira.')
            } else {
                alert('Erro ao carregar a feira.')
            }
            navigate('/feiras', { replace: true })
            return false
        }
    }

    const scanQRCode = () => {
        if (!videoRef.current || !canvasRef.current || !webcamActive) return

        const video = videoRef.current
        const canvas = canvasRef.current
        const ctx = canvas.getContext('2d')

        if (video.readyState !== video.HAVE_ENOUGH_DATA) {
            animationFrameRef.current = requestAnimationFrame(scanQRCode)
            return
        }

        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
        const code = jsQR(imageData.data, imageData.width, imageData.height, {
            inversionAttempts: 'dontInvert',
        })

        if (code) {
            setScanning(false)
            consultarNota(code.data)
            return
        }

        animationFrameRef.current = requestAnimationFrame(scanQRCode)
    }

    useEffect(() => {
        const iniciar = async () => {
            try {
                const ok = await validarFeira()
                if (ok) {
                    startWebcam()
                }
            } catch (error) {
                console.error('Erro na inicialização ScanNFCe:', error)
                setRouterError(error)
            }
        }
        iniciar()
        return () => {
            stopWebcam()
        }
    }, [id])

    useEffect(() => {
        if (webcamActive && scanning) {
            animationFrameRef.current = requestAnimationFrame(scanQRCode)
        }
        return () => {
            if (animationFrameRef.current) {
                cancelAnimationFrame(animationFrameRef.current)
            }
        }
    }, [webcamActive, scanning])

    const startWebcam = async () => {
        if (streamRef.current) return

        if (!navigator.mediaDevices?.getUserMedia) {
            setCameraSupported(false)
            return
        }

        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: { ideal: 'environment' } }
            })
            streamRef.current = stream
            if (videoRef.current) {
                videoRef.current.srcObject = stream
            }
            setWebcamActive(true)
            setCameraSupported(true)
            setScanning(true)
        } catch (error) {
            console.error(error)
            setWebcamActive(false)
            setCameraSupported(false)
            setScanning(false)
        }
    }

    const stopWebcam = () => {
        setScanning(false)
        if (animationFrameRef.current) {
            cancelAnimationFrame(animationFrameRef.current)
            animationFrameRef.current = null
        }
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop())
            streamRef.current = null
        }
        if (videoRef.current) {
            videoRef.current.srcObject = null
        }
        setWebcamActive(false)
    }

    const handleSubmitManual = async (e) => {
        e.preventDefault()
        setError('')

        const chave = chaveManual.trim().replace(/\s/g, '')

        if (!chave) {
            setError('Digite a chave de acesso da nota fiscal')
            return
        }

        if (!/^[0-9A-Za-z]{44}$/.test(chave)) {
            setError('A chave de acesso deve ter exatamente 44 dígitos')
            return
        }

        await consultarNota(chave)
    }

    const consultarNota = async (qrData) => {
        const ok = await validarFeira()
        if (!ok) return

        setProcessing(true)
        setError('')
        setDadosNota(null)
        setComparacao(null)

        try {
            const response = await api.post('/nfce/consultar', {
                feira_id: parseInt(id),
                qr_code: qrData,
                consentimento_lgpd: true
            })

            setDadosNota(response.data)
            setComparacao(response.data?.comparacao || null)
            navigate(`/feira/${id}/comparacao`, {
                state: { comparacao: response.data }
            })
        } catch (error) {
            console.error('Erro ao consultar nota:', error)
            const mensagem = error.response?.data?.detail || 'Erro ao consultar nota fiscal. Tente novamente.'
            setError(mensagem)
        } finally {
            setProcessing(false)
        }
    }

    const handleBack = () => {
        stopWebcam()
        navigate(`/feira/${id}`, { replace: true })
    }

    if (routerError) {
        return (
            <div className="scan-nfce-container">
                <header className="scan-nfce-header">
                    <button className="btn-back" onClick={() => navigate('/feiras', { replace: true })} aria-label="Voltar">
                        <IoArrowBack />
                    </button>
                    <h1>Escanear NFCe</h1>
                </header>
                <div className="scan-nfce-content">
                    <div className="scan-nfce-error">
                        Erro ao carregar o scanner. Tenta novamente mais tarde.
                    </div>
                </div>
            </div>
        )
    }

    if (dadosNota) {
        const comp = comparacao || {}
        const resumo = comp.resumo || {}
        const naoEncontrados = resumo.nao_encontrados || []
        const adicionais = resumo.adicionais || []
        const itensComparacao = comp.itens || []
        const totalDivergencias = itensComparacao.filter((item) => item.divergente).length

        return (
            <div className="scan-nfce-container">
                <header className="scan-nfce-header">
                    <button className="btn-back" onClick={handleBack} aria-label="Voltar">
                        <IoArrowBack />
                    </button>
                    <h1>Resultado da Compra</h1>
                </header>

                <div className="scan-nfce-content">
                    <div className="scan-nfce-instruction">
                        <p>
                            {comp.mercado || dadosNota.mercado || 'Mercado'} •{' '}
                            {(comp.data_compra || dadosNota.data_compra || '').slice(0, 10)}
                        </p>
                    </div>

                    <div className="scan-nfce-cards">
                        <div className="scan-nfce-card ok">
                            <span className="scan-nfce-card-valor">{itensComparacao.length - totalDivergencias}</span>
                            <span className="scan-nfce-card-label">Conferidos</span>
                        </div>
                        <div className="scan-nfce-card divergencia">
                            <span className="scan-nfce-card-valor">{totalDivergencias}</span>
                            <span className="scan-nfce-card-label">Divergências</span>
                        </div>
                        <div className="scan-nfce-card nao-encontrado">
                            <span className="scan-nfce-card-valor">{naoEncontrados.length}</span>
                            <span className="scan-nfce-card-label">Na Lista, Não na Nota</span>
                        </div>
                        <div className="scan-nfce-card adicional">
                            <span className="scan-nfce-card-valor">{adicionais.length}</span>
                            <span className="scan-nfce-card-label">Na Nota, Não na Lista</span>
                        </div>
                    </div>

                    <div className="scan-nfce-totais">
                        <div className="scan-nfce-total-item economia">
                            <span className="scan-nfce-total-label">Economia</span>
                            <span className="scan-nfce-total-valor">
                                R$ {(comp.economia || 0).toFixed(2).replace('.', ',')}
                            </span>
                        </div>
                        <div className="scan-nfce-total-item prejuizo">
                            <span className="scan-nfce-total-label">Prejuízo</span>
                            <span className="scan-nfce-total-valor">
                                R$ {(comp.prejuizo || 0).toFixed(2).replace('.', ',')}
                            </span>
                        </div>
                    </div>

                    <button
                        className="scan-nfce-submit scan-nfce-submit-full"
                        onClick={handleBack}
                        disabled={processing}
                    >
                        Voltar para feira
                    </button>
                </div>
            </div>
        )
    }

    return (
        <div className="scan-nfce-container">
            <header className="scan-nfce-header">
                <button className="btn-back" onClick={handleBack} aria-label="Voltar">
                    <IoArrowBack />
                </button>
                <h1>Escanear NFCe</h1>
            </header>

            {processing && (
                <div className="scan-nfce-loading">
                    <div className="spinner"></div>
                    <p>Consultando nota fiscal...</p>
                    <p className="loading-sub">Isso pode levar alguns segundos</p>
                </div>
            )}

            <div className="scan-nfce-content">
                <div className="scan-nfce-camera-section">
                    <div className="scan-nfce-instruction">
                        <IoQrCode size={32} />
                        <p>{scanning ? 'Escaneando... Posicione o QR Code' : 'Posicione o QR Code da nota fiscal'}</p>
                    </div>

                    <div className="scan-nfce-camera-area">
                        {webcamActive ? (
                            <video
                                ref={videoRef}
                                autoPlay
                                playsInline
                                className="scan-nfce-video"
                            />
                        ) : (
                            <div className="scan-nfce-camera-placeholder">
                                <p>Câmera indisponível</p>
                            </div>
                        )}
                    </div>
                </div>

                <div className="scan-nfce-divider">
                    <span>ou digite a chave de acesso</span>
                </div>

                <form className="scan-nfce-manual-form" onSubmit={handleSubmitManual}>
                    <div className="scan-nfce-input-group">
                        <input
                            type="text"
                            className="scan-nfce-input"
                            value={chaveManual}
                            onChange={(e) => {
                                const value = e.target.value.replace(/[^0-9A-Za-z]/g, '').slice(0, 44)
                                setChaveManual(value)
                                if (error) setError('')
                            }}
                            placeholder="Cole ou digite os 44 dígitos"
                            maxLength={44}
                            disabled={processing}
                        />
                        <span className="scan-nfce-input-hint">
                            {chaveManual.length}/44 dígitos
                        </span>
                    </div>

                    {error && (
                        <div className="scan-nfce-error">
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        className="scan-nfce-submit"
                        disabled={processing || chaveManual.length !== 44}
                    >
                        {processing ? 'Consultando...' : 'Consultar Nota'}
                    </button>
                </form>

                <button
                    className="scan-nfce-cancel"
                    onClick={handleBack}
                    disabled={processing}
                >
                    Cancelar
                </button>
            </div>

            <canvas
                ref={canvasRef}
                style={{ display: 'none' }}
            />
        </div>
    )
}

export default ScanNFCe
