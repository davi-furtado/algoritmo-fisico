import { useEffect, useMemo, useRef, useState } from 'react'
import { View, Text, TouchableOpacity, Animated, Easing } from 'react-native'

export default function SegmentedToggle({
  options,
  value,
  onChange,
  style,
  textStyle,
  activeTextStyle
}) {
  const [width, setWidth] = useState(0)
  const anim = useRef(new Animated.Value(0)).current

  const index = useMemo(() => {
    const i = options.findIndex(o => o.key === value)
    return i < 0 ? 0 : i
  }, [options, value])

  useEffect(() => {
    Animated.timing(anim, {
      toValue: index,
      duration: 90,
      easing: Easing.out(Easing.quad),
      useNativeDriver: true
    }).start()
  }, [index, anim])

  const onLayout = e => setWidth(e.nativeEvent.layout.width)
  const itemWidth = width > 0 ? width / options.length : 0

  const translateX = anim.interpolate({
    inputRange: [0, options.length - 1],
    outputRange: [0, itemWidth * (options.length - 1)]
  })

  return (
    <View
      onLayout={onLayout}
      style={[
        {
          height: 44,
          borderRadius: 999,
          backgroundColor: '#1a1a1a',
          padding: 4,
          flexDirection: 'row',
          alignItems: 'center',
          position: 'relative',
          overflow: 'hidden'
        },
        style
      ]}
    >
      {width > 0 && (
        <Animated.View
          pointerEvents='none'
          style={{
            position: 'absolute',
            left: 4,
            top: 4,
            bottom: 4,
            width: itemWidth - 8,
            borderRadius: 999,
            backgroundColor: '#2c2c2c',
            transform: [{ translateX }]
          }}
        />
      )}

      {options.map(opt => {
        const active = opt.key === value
        return (
          <TouchableOpacity
            key={opt.key}
            style={{
              flex: 1,
              height: '100%',
              borderRadius: 999,
              alignItems: 'center',
              justifyContent: 'center'
            }}
            activeOpacity={0.85}
            onPress={() => onChange(opt.key)}
          >
            <Text
              style={[
                { color: '#dcdcdc', fontWeight: '700', fontSize: 15 },
                textStyle,
                active && [{ color: '#ffffff' }, activeTextStyle]
              ]}
              numberOfLines={1}
            >
              {opt.label}
            </Text>
          </TouchableOpacity>
        )
      })}
    </View>
  )
}
