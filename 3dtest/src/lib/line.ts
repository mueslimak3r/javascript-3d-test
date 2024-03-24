import { Vector3 } from 'three'

const lines: Vector3[][] = []
for (let index = 0; index < 10; index++) {
    const points: Vector3[] = []
    for (let index = 0; index < 3; index++) {
        const point = new Vector3(25 - Math.random() * 50, 25 - Math.random() * 50, 25 - Math.random() * 50)
        points.push(point)
    }
    lines.push(points)
}

export const getRandomColor = () => {
    return `#${Math.floor(Math.random() * 16777215).toString(16)}`
}

export const getLines = () => { return lines }