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

  const sendImage = useCallback(async uri => {
    setLoading(true)

    let ext = uri.split('.').pop()?.split('?')[0]?.toLowerCase()
    if (ext?.includes('/') || ext?.includes('\\') || ext === 'data') {
      ext = undefined
    }

    const mimeMap = {
      jpg: 'image/jpeg',
      jpeg: 'image/jpeg',
      png: 'image/png',
      webp: 'image/webp',
      bmp: 'image/bmp'
    }

    const filename = `image.${ext || 'jpg'}`
    const mimeType = mimeMap[ext] || 'image/jpeg'

    const form = new FormData()

    if (Platform.OS === 'web') {
      try {
        const response = await fetch(uri)
        const blobData = await response.blob()
        form.append('file', blobData, filename)
      } catch (err) {
        setOutput(`Erro ao processar imagem na web: ${err.message}`)
        setIsError(true)
        setLoading(false)
        return
      }
    } else {
      const fileData = {
        uri,
        name: filename,
        type: mimeType
      }
      form.append('file', fileData)
    }

    try {
      const res = await fetchWithTimeout(url, {
        method: 'POST',
        body: form,
        headers: { Accept: 'application/json' }
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
        let errorText = ''
        try {
          const errorJson = await res.json()

          if (errorJson.detail) {
            errorText =
              typeof errorJson.detail === 'object'
                ? JSON.stringify(errorJson.detail, null, 2)
                : errorJson.detail
          } else {
            errorText = JSON.stringify(errorJson, null, 2)
          }
        } catch {
          errorText = await res.text()
        }

        setOutput(`Erro ${res.status}:\n${errorText}`)
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
          <>
            <InsertPhotoBtn
              text='Câmera'
              onPress={pickImage}
              isMobile
            />
            <InsertPhotoBtn
              text='Galeria'
              onPress={pickImage}
            />
          </>
        )}
        {Platform.OS === 'web' && (
          <InsertPhotoBtn
            text='Upload image'
            onPress={pickImage}
          />
        )}
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
