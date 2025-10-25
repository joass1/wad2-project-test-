/**
 * TMX/TSX Parser for Tiled Map Editor files
 * Loads and parses TMX map files and TSX tileset files
 */

/**
 * Load and parse a TSX (Tileset) file
 * @param {string} tsxPath - Path to the TSX file
 * @returns {Promise<Object>} Parsed tileset data
 */
export async function loadTileset(tsxPath) {
  try {
    // Add cache-busting timestamp
    const cacheBuster = `?t=${Date.now()}`
    const fullPath = tsxPath + cacheBuster
    const response = await fetch(fullPath)

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    const xmlText = await response.text()
    const parser = new DOMParser()
    const xmlDoc = parser.parseFromString(xmlText, 'text/xml')

    // Check for XML parsing errors
    const parserError = xmlDoc.querySelector('parsererror')
    if (parserError) {
      throw new Error('XML parsing error: ' + parserError.textContent)
    }

    const tilesetElement = xmlDoc.querySelector('tileset')
    if (!tilesetElement) {
      throw new Error('No <tileset> element found in TSX file')
    }

    const columns = parseInt(tilesetElement.getAttribute('columns'))

    // Check if this is a collection tileset (columns=0, individual tile images)
    const isCollectionTileset = columns === 0

    if (isCollectionTileset) {
      // Collection tileset - each tile has its own image
      const tiles = []
      const tileElements = tilesetElement.querySelectorAll('tile')

      for (const tileEl of tileElements) {
        const tileId = parseInt(tileEl.getAttribute('id'))
        const imageEl = tileEl.querySelector('image')
        if (imageEl) {
          tiles.push({
            id: tileId,
            imageSource: imageEl.getAttribute('source'),
            width: parseInt(imageEl.getAttribute('width')),
            height: parseInt(imageEl.getAttribute('height'))
          })
        }
      }

      return {
        name: tilesetElement.getAttribute('name'),
        tileWidth: parseInt(tilesetElement.getAttribute('tilewidth')),
        tileHeight: parseInt(tilesetElement.getAttribute('tileheight')),
        tileCount: parseInt(tilesetElement.getAttribute('tilecount')),
        columns: 0,
        isCollection: true,
        tiles // Individual tile definitions
      }
    } else {
      // Regular tileset with single spritesheet
      const imageElement = tilesetElement.querySelector('image')
      if (!imageElement) {
        throw new Error('No <image> element found in tileset')
      }

      return {
        name: tilesetElement.getAttribute('name'),
        tileWidth: parseInt(tilesetElement.getAttribute('tilewidth')),
        tileHeight: parseInt(tilesetElement.getAttribute('tileheight')),
        tileCount: parseInt(tilesetElement.getAttribute('tilecount')),
        columns: columns,
        isCollection: false,
        imageSource: imageElement.getAttribute('source'),
        imageWidth: parseInt(imageElement.getAttribute('width')),
        imageHeight: parseInt(imageElement.getAttribute('height'))
      }
    }
  } catch (error) {
    console.error(`Failed to load tileset: ${tsxPath}`, error)
    throw error
  }
}

/**
 * Load and parse a TMX (Map) file
 * @param {string} tmxPath - Path to the TMX file
 * @returns {Promise<Object>} Parsed map data
 */
export async function loadTMXMap(tmxPath) {
  try {
    // Add cache-busting timestamp to force reload
    const cacheBuster = `?t=${Date.now()}`
    const fullPath = tmxPath + cacheBuster
    console.log('TMX Parser: Loading TMX from', fullPath)
    const response = await fetch(fullPath)

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    const xmlText = await response.text()
    const parser = new DOMParser()
    const xmlDoc = parser.parseFromString(xmlText, 'text/xml')

    // Check for XML parsing errors
    const parserError = xmlDoc.querySelector('parsererror')
    if (parserError) {
      throw new Error('XML parsing error: ' + parserError.textContent)
    }

    const mapElement = xmlDoc.querySelector('map')
    if (!mapElement) {
      throw new Error('No <map> element found in TMX file')
    }

    // Parse map properties
    const mapData = {
      width: parseInt(mapElement.getAttribute('width')),
      height: parseInt(mapElement.getAttribute('height')),
      tileWidth: parseInt(mapElement.getAttribute('tilewidth')),
      tileHeight: parseInt(mapElement.getAttribute('tileheight')),
      tilesets: [],
      layers: [],
      objectGroups: []
    }

    // Parse tilesets
    const tilesetElements = xmlDoc.querySelectorAll('tileset')
    const baseDir = tmxPath.substring(0, tmxPath.lastIndexOf('/') + 1)
    console.log('TMX Parser: Base directory:', baseDir)
    console.log('TMX Parser: Found', tilesetElements.length, 'tilesets')

    for (const tilesetEl of tilesetElements) {
      const firstGid = parseInt(tilesetEl.getAttribute('firstgid'))
      const source = tilesetEl.getAttribute('source')

      if (source) {
        // External tileset - load it
        const tsxPath = baseDir + source
        console.log('TMX Parser: Loading tileset from', tsxPath)
        const tilesetData = await loadTileset(tsxPath)

        if (tilesetData.isCollection) {
          // Collection tileset - need to resolve paths for all tile images
          const tilesWithPaths = tilesetData.tiles.map(tile => ({
            ...tile,
            imagePath: baseDir + tile.imageSource
          }))
          console.log('TMX Parser: Collection tileset with', tilesWithPaths.length, 'tiles')
          mapData.tilesets.push({
            firstGid,
            ...tilesetData,
            tiles: tilesWithPaths
          })
        } else {
          // Regular tileset - single image path
          const imagePath = baseDir + tilesetData.imageSource
          console.log('TMX Parser: Tileset image path:', imagePath)
          mapData.tilesets.push({
            firstGid,
            ...tilesetData,
            imagePath
          })
        }
      }
    }

    // Parse layers
    const layerElements = xmlDoc.querySelectorAll('layer')
    for (const layerEl of layerElements) {
      const layer = {
        id: layerEl.getAttribute('id'),
        name: layerEl.getAttribute('name'),
        width: parseInt(layerEl.getAttribute('width')),
        height: parseInt(layerEl.getAttribute('height')),
        data: []
      }

      // Parse CSV data
      const dataElement = layerEl.querySelector('data')
      const encoding = dataElement.getAttribute('encoding')

      if (encoding === 'csv') {
        const csvText = dataElement.textContent.trim()
        const rows = csvText.split('\n')
        for (const row of rows) {
          const tiles = row.split(',').map(t => parseInt(t.trim()))
          layer.data.push(tiles)
        }
      }

      mapData.layers.push(layer)
    }

    // Parse object groups (for collision, trees, etc.)
    const objectGroupElements = xmlDoc.querySelectorAll('objectgroup')
    for (const objGroupEl of objectGroupElements) {
      const objectGroup = {
        id: objGroupEl.getAttribute('id'),
        name: objGroupEl.getAttribute('name'),
        objects: []
      }

      const objectElements = objGroupEl.querySelectorAll('object')
      for (const objEl of objectElements) {
        const obj = {
          id: objEl.getAttribute('id'),
          x: parseFloat(objEl.getAttribute('x')) || 0,
          y: parseFloat(objEl.getAttribute('y')) || 0,
          width: parseFloat(objEl.getAttribute('width')) || 0,
          height: parseFloat(objEl.getAttribute('height')) || 0,
          gid: objEl.getAttribute('gid') ? parseInt(objEl.getAttribute('gid')) : null
        }
        objectGroup.objects.push(obj)
      }

      mapData.objectGroups.push(objectGroup)
    }

    return mapData
  } catch (error) {
    console.error(`Failed to load TMX map: ${tmxPath}`, error)
    throw error
  }
}

/**
 * Get tileset for a given GID (Global ID)
 * @param {number} gid - Global tile ID
 * @param {Array} tilesets - Array of tileset data
 * @returns {Object|null} Tileset data and local tile ID
 */
export function getTilesetForGid(gid, tilesets) {
  if (gid === 0) return null // 0 means empty tile

  // Sort tilesets by firstGid in descending order
  const sortedTilesets = [...tilesets].sort((a, b) => b.firstGid - a.firstGid)

  for (const tileset of sortedTilesets) {
    if (gid >= tileset.firstGid) {
      return {
        tileset,
        localId: gid - tileset.firstGid
      }
    }
  }

  return null
}

/**
 * Calculate source rectangle for a tile in a tileset
 * @param {number} localId - Local tile ID within the tileset
 * @param {Object} tileset - Tileset data
 * @returns {Object} Source rectangle {x, y, width, height}
 */
export function getTileSourceRect(localId, tileset) {
  const col = localId % tileset.columns
  const row = Math.floor(localId / tileset.columns)

  return {
    x: col * tileset.tileWidth,
    y: row * tileset.tileHeight,
    width: tileset.tileWidth,
    height: tileset.tileHeight
  }
}
