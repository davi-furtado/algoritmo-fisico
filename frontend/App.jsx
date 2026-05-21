import { useState, useCallback } from 'react'
import {
  View,
  Text,
  Image,
  TouchableOpacity,
  ActivityIndicator,
  ScrollView,
  Modal,
  Platform
} from 'react-native'
import * as ImagePicker from 'expo-image-picker'
import { useFonts } from 'expo-font'

import styles from './styles'
import InsertPhotoBtn from './components/InsertPhotoBtn'
import CodeBox from './components/CodeBox'
import SegmentedToggle from './components/SegmentedToggle'

const url = 'http://SEU_IP_AQUI:8000/'

export default function App() {
  const [image, setImage] = useState(null)
  const [json, setJson] = useState('')
  const [pseudocode, setPseudocode] = useState('')
  const [python, setPython] = useState('')
  const [output, setOutput] = useState('')
  const [isError, setIsError] = useState(false)
  const [view, setView] = useState('pseudo')
  const [loading, setLoading] = useState(false)
  const [zoom, setZoom] = useState(false)

  const [fontsLoaded] = useFonts({
    JetBrainsMono: require('./assets/JetBrainsMonoNL-Bold.ttf')
  })

  const monoFamily = fontsLoaded
    ? 'JetBrainsMono'
    : Platform.select({
        ios: 'Menlo',
        android: 'monospace',
        default: 'Courier'
      })

  const fetchWithTimeout = async (resource, options = {}) => {
    const { timeout = 20000, ...fetchOptions } = options
    const controller = new AbortController()
    const id = setTimeout(() => controller.abort(), timeout)
    try {
      return await fetch(resource, {
        ...fetchOptions,
        signal: controller.signal
      })
    } finally {
      clearTimeout(id)
    }
  }

  const dataUrlToBlob = dataUrl => {
    const [header, data] = dataUrl.split(',')
    const mimeMatch = header.match(/:(.*?);/)
    const mime = mimeMatch ? mimeMatch[1] : 'image/jpeg'
    const binary = atob(data)
    const array = new Uint8Array(binary.length)
    for (let i = 0; i < binary.length; i += 1) {
      array[i] = binary.charCodeAt(i)
    }
    return new Blob([array], { type: mime })
  }

  const sendImage = useCallback(async uri => {
    setLoading(true)

    let ext = uri.split('.').pop()?.split('?')[0]?.toLowerCase()
    if (
      ext?.includes('/') ||
      ext?.includes('\\') ||
      ext === 'blob' ||
      ext === 'data'
    ) {
      ext = undefined
    }

    const mimeMap = {
      jpg: 'image/jpeg',
      jpeg: 'image/jpeg',
      png: 'image/png',
      webp: 'image/webp',
      bmp: 'image/bmp'
    }

    let filename = `image.${ext || 'jpg'}`
    let filePayload = {
      uri,
      name: filename,
      type: mimeMap[ext] || 'image/jpeg'
    }

    if (Platform.OS === 'web') {
      let blob
      if (uri.startsWith('data:')) {
        blob = dataUrlToBlob(uri)
      } else {
        const response = await fetchWithTimeout(uri, { timeout: 15000 })
        if (!response.ok) {
          throw new Error(
            `Não foi possível carregar a imagem local: ${response.status}`
          )
        }
        blob = await response.blob()
      }
      const blobExt = blob.type.split('/').pop()?.toLowerCase()
      const normalizedExt = blobExt === 'jpeg' ? 'jpg' : blobExt || 'jpg'
      const normalizedMime = blob.type || mimeMap[ext] || 'image/jpeg'
      filename = `image.${normalizedExt}`
      filePayload = blob
      filePayload.name = filename
      filePayload.type = normalizedMime
    }

    const form = new FormData()
    if (Platform.OS === 'web') {
      form.append('file', filePayload, filename)
    } else {
      form.append('file', filePayload)
    }

    try {
      const res = await fetchWithTimeout(url, {
        method: 'POST',
        body: form,
        headers: {
          'Content-Type': 'multipart/form-data',
          Accept: 'application/json'
        }
      })
      if (res.status === 200) {
        const data = await res.json()
        setJson(JSON.stringify(data, null, 2))
        if (data.error) {
          setOutput(data.error || 'Erro desconhecido')
          setIsError(true)
          setPseudocode('')
          setPython('')
        } else {
          setPseudocode(data.pseudocode || '')
          setPython(data.python || '')
          setOutput(data.output || '')
          setIsError(false)
        }
      } else {
        let errorText = await res.text()
        try {
          const errorJson = JSON.parse(errorText)
          errorText = errorJson.detail || errorJson.error || errorText
        } catch {
          // manter raw text se não for JSON
        }
        setOutput(
          `Erro ${res.status}: ${
            errorText || res.statusText || 'Resposta inesperada do servidor'
          }`
        )
        setIsError(true)
        setPseudocode('')
        setPython('')
      }
    } catch (e) {
      setOutput(`Erro ao conectar com o servidor: ${e.message}`)
      setIsError(true)
      setPseudocode('')
      setPython('')
    } finally {
      setLoading(false)
    }
  }, [])

  const pickImage = useCallback(
    async camera => {
      const result = camera
        ? await ImagePicker.launchCameraAsync({
            quality: 1,
            allowsEditing: false
          })
        : await ImagePicker.launchImageLibraryAsync({
            quality: 1,
            allowsEditing: false
          })
      if (!result.canceled && result.assets?.length) {
        const uri = result.assets[0].uri
        setImage(uri)
        sendImage(uri)
      }
    },
    [sendImage]
  )

  const code = view === 'pseudo' ? pseudocode || '' : python || ''

  return (
    <ScrollView style={styles.container}>
      <View style={styles.row}>
        {Platform.OS !== 'web' && (
          <InsertPhotoBtn
            text='Câmera'
            onPress={pickImage}
            isMobile
          />
        )}
        <InsertPhotoBtn
          text='Galeria'
          onPress={pickImage}
        />
      </View>

      {image && (
        <>
          <TouchableOpacity
            onPress={() => setZoom(true)}
            activeOpacity={0.7}
          >
            <Image
              source={{ uri: image }}
              style={styles.image}
            />
          </TouchableOpacity>

          <Modal
            visible={zoom}
            animationType='fade'
            onRequestClose={() => setZoom(false)}
            transparent={false}
          >
            <ScrollView
              maximumZoomScale={5}
              minimumZoomScale={1}
              contentContainerStyle={styles.scroll}
              style={{ flex: 1, backgroundColor: '#000' }}
            >
              <Image
                source={{ uri: image }}
                style={styles.full}
                resizeMode='contain'
              />
            </ScrollView>

            <View style={styles.modalBtnWrapper}>
              <TouchableOpacity
                style={styles.modalBtn}
                activeOpacity={0.7}
                onPress={() => setZoom(false)}
              >
                <Text style={styles.modalBtnText}>Fechar</Text>
              </TouchableOpacity>
            </View>
          </Modal>
        </>
      )}

      {loading && (
        <ActivityIndicator
          size='large'
          color='#fff'
          style={{ marginTop: 20 }}
        />
      )}

      {output !== '' && (
        <CodeBox
          title={isError ? 'Erro' : 'Saída'}
          text={output.trim()}
          maxHeight={240}
          monoFamily={monoFamily}
        />
      )}

      {(pseudocode !== '' || python !== '') && (
        <>
          <SegmentedToggle
            options={[
              { key: 'pseudo', label: 'Pseudocódigo' },
              { key: 'python', label: 'Python' }
            ]}
            value={view}
            onChange={setView}
            style={styles.segmentedWrap}
            textStyle={styles.segmentedText}
            activeTextStyle={styles.segmentedTextActive}
          />

          <CodeBox
            title={view === 'pseudo' ? 'Pseudocódigo' : 'Python'}
            text={code}
            maxHeight={320}
            monoFamily={monoFamily}
          />
        </>
      )}
    </ScrollView>
  )
}
