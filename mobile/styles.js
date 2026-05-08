import { StyleSheet, Platform } from 'react-native'

export default StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
    padding: 12
  },
  row: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 50
  },
  btn: {
    backgroundColor: '#1760ff',
    padding: 12,
    flex: 1,
    borderRadius: 8
  },
  btnText: {
    color: '#fff',
    textAlign: 'center',
    fontWeight: 'bold',
    fontSize: 20
  },
  image: {
    width: '100%',
    height: 300,
    marginTop: 9,
    borderRadius: 8
  },
  full: {
    width: '100%',
    height: '100%',
    backgroundColor: '#000'
  },
  scroll: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center'
  },
  codeBox: {
    marginTop: 16,
    padding: 12,
    backgroundColor: '#222528',
    borderRadius: 8
  },
  codeTitle: {
    color: '#bfbfbf',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8
  },
  code: {
    color: '#0f0',
    fontSize: 16
  },
  segmentedWrap: {
    marginTop: 16
  },
  segmentedText: {
    fontSize: 15,
    fontWeight: '700',
    color: '#dcdcdc'
  },
  segmentedTextActive: {
    color: '#ffffff'
  },
  modalBtnWrapper: {
    position: 'absolute',
    left: 0,
    right: 0,
    bottom: Platform.select({ ios: 24, android: 16, default: 16 }),
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 16
  },
  modalBtn: {
    backgroundColor: '#e53935',
    paddingVertical: 12,
    paddingHorizontal: 24,
    minWidth: 140,
    borderRadius: 999,
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 2
  },
  modalBtnText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 18
  }
})
