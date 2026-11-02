// =====================================================
// MAP GENERATOR
// Builds a new random map for every game: the village in the middle,
// muddy water holes close by, clean water far away, and trees everywhere else.
//
// The map is a list of objects like { type: 'house', x: 1180, y: 860 },
// the same shape renderWorld() in script.js already knows how to draw.
//
// This file is loaded BEFORE script.js (see index.html), but it uses a few
// things from script.js: WORLD_WIDTH, WORLD_HEIGHT, HOME_POSITION and getDistance().
// That's fine, because nothing here runs until script.js calls generateMap(),
// and by then both files have finished loading.
// =====================================================

// ---------- Settings (change these to change what maps look like) ----------

const HOUSE_COUNT = 8;
const VILLAGE_RADIUS = 200; // houses are built within this distance of the village center

const DIRTY_POND_COUNT = 2;
const DIRTY_POND_DISTANCE = { min: 250, max: 450 }; // a short walk from the village

const CLEAN_POND_COUNT = 5;
const CLEAN_POND_DISTANCE = { min: 650, max: 820 }; // a long walk from the village

const TREE_COUNT = 80;
const TREE_FREE_RADIUS = 260; // no trees this close to the village center

const EDGE_MARGIN = 80; // keep everything this far from the edge of the world
const MAX_TRIES = 200;  // how many random spots to try before giving up on an object

// How much empty space each type of object needs around it, measured from its x/y.
// Two objects must be at least their two ROOMs apart (a house and a tree: 38 + 26 = 64 pixels).
// These are big enough that there's always a gap wider than the player between any
// two footprints (see OBJECT_TYPES in script.js), so the player can never get walled in.
const ROOM = {
    house: 38,
    tree: 26,
    pump: 20,
    'water-hole': 95,
    'dirty-hole': 95
};

// The player starts at HOME_POSITION every morning, so keep this much space clear around it
const HOME_ROOM = 20;

const FULL_CIRCLE = Math.PI * 2; // a full turn, in radians (360 degrees)

// ---------- Random numbers you can replay ----------

// Math.random() gives different numbers every time. This random() gives the SAME
// list of numbers every time you start from the same "seed" number, so the same
// seed always builds the same map. That's very handy when a map has a bug:
// add ?seed=12345 to the end of the page address to play that exact map again.
let randomSeed = 1;

function setRandomSeed(seed) {
    randomSeed = seed;
}

// Returns a number from 0 up to (but not including) 1, like Math.random().
// This is a small, well-known formula called "mulberry32". You don't need to follow
// the math: it just scrambles the seed into a new, random-looking number each time.
function random() {
    randomSeed = (randomSeed + 0x6D2B79F5) | 0;
    let t = randomSeed;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
}

// A random number between min and max
function randomBetween(min, max) {
    return min + random() * (max - min);
}

// ---------- Picking spots ----------

// The spot you reach by walking `distance` pixels from `center` in the direction `angle`.
// (Math.cos and Math.sin turn a direction into how far to go across and down.)
function spotAround(center, angle, distance) {
    return {
        x: center.x + Math.cos(angle) * distance,
        y: center.y + Math.sin(angle) * distance
    };
}

// A random spot anywhere in the world (not too close to the edge)
function randomSpotAnywhere() {
    return {
        x: randomBetween(EDGE_MARGIN, WORLD_WIDTH - EDGE_MARGIN),
        y: randomBetween(EDGE_MARGIN, WORLD_HEIGHT - EDGE_MARGIN)
    };
}

// A random spot anywhere, except in the village clearing
function randomSpotOutsideVillage() {
    let spot = randomSpotAnywhere();
    while (getDistance(spot, HOME_POSITION) < TREE_FREE_RADIUS) {
        spot = randomSpotAnywhere(); // too close to the village: try again
    }
    return spot;
}

// Is there enough empty space for a new object of this type at this spot?
function hasRoom(map, type, spot) {
    // Not too close to the edge of the world
    if (spot.x < EDGE_MARGIN || spot.x > WORLD_WIDTH - EDGE_MARGIN ||
        spot.y < EDGE_MARGIN || spot.y > WORLD_HEIGHT - EDGE_MARGIN) {
        return false;
    }

    // Not on top of the spot where the player starts
    if (getDistance(spot, HOME_POSITION) < ROOM[type] + HOME_ROOM) {
        return false;
    }

    // Not too close to anything already on the map.
    // .every() is true only if EVERY item passes the test.
    return map.every((item) => getDistance(item, spot) >= ROOM[item.type] + ROOM[type]);
}

// Try random spots until one has room for this type of object. This is called
// "rejection sampling": pick at random, reject the bad picks, try again.
// pickSpot is a function that returns a random spot (like randomSpotAnywhere).
// Returns the spot, or null if there was no room after MAX_TRIES tries.
function findSpot(map, type, pickSpot) {
    for (let tries = 0; tries < MAX_TRIES; tries++) {
        const spot = pickSpot();
        if (hasRoom(map, type, spot)) {
            // Whole pixels keep the pixel art sharp
            return { x: Math.round(spot.x), y: Math.round(spot.y) };
        }
    }
    return null;
}

// Find a spot for an object and add it to the map
function placeObject(map, type, pickSpot) {
    const spot = findSpot(map, type, pickSpot);
    if (spot) {
        map.push({ type: type, x: spot.x, y: spot.y });
    }
}

// ---------- Building the map ----------

// Build a whole new map from a seed. The same seed always builds the same map.
function generateMap(seed) {
    setRandomSeed(seed);
    const map = [];

    // 1. Houses, scattered around the village center
    for (let i = 0; i < HOUSE_COUNT; i++) {
        placeObject(map, 'house', () =>
            spotAround(HOME_POSITION, randomBetween(0, FULL_CIRCLE), randomBetween(70, VILLAGE_RADIUS))
        );
    }

    // 2. Clean water holes, far away. To spread them out in different directions,
    //    split the circle into equal slices (like a pizza) and put one in each slice,
    //    with a little wobble so they don't look lined up.
    const startAngle = randomBetween(0, FULL_CIRCLE);
    for (let i = 0; i < CLEAN_POND_COUNT; i++) {
        const sliceAngle = startAngle + i * (FULL_CIRCLE / CLEAN_POND_COUNT);
        placeObject(map, 'water-hole', () =>
            spotAround(HOME_POSITION, sliceAngle + randomBetween(-0.3, 0.3), randomBetween(CLEAN_POND_DISTANCE.min, CLEAN_POND_DISTANCE.max))
        );
    }

    // 3. Muddy water holes, temptingly close to the village
    for (let i = 0; i < DIRTY_POND_COUNT; i++) {
        placeObject(map, 'dirty-hole', () =>
            spotAround(HOME_POSITION, randomBetween(0, FULL_CIRCLE), randomBetween(DIRTY_POND_DISTANCE.min, DIRTY_POND_DISTANCE.max))
        );
    }

    // 4. Trees fill in the rest. They go last, so they fit around everything else.
    for (let i = 0; i < TREE_COUNT; i++) {
        placeObject(map, 'tree', randomSpotOutsideVillage);
    }

    return map;
}
