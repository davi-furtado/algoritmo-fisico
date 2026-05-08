import { View, Text, ScrollView } from 'react-native'
import styles from '../styles'

export default function CodeBox({ title, text, maxHeight = 320, monoFamily }) {
  return (
    <View style={styles.codeBox}>
      {title ? <Text style={styles.codeTitle}>{title}</Text> : null}
      <ScrollView
        style={{ maxHeight }}
        nestedScrollEnabled
        showsVerticalScrollIndicator
      >
        <ScrollView
          horizontal
          bounces={false}
          nestedScrollEnabled
          showsHorizontalScrollIndicator
        >
          <Text
            style={[styles.code, { fontFamily: monoFamily }]}
            selectable
          >
            {text || ''}
          </Text>
        </ScrollView>
      </ScrollView>
    </View>
  )
}
