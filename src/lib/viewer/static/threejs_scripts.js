let jsFiles = [];
let selectedJs = null;
let feedbackData = {};
let isClosing = false;
let selectedIndex = -1;
let isTyping = false;
let scenes = {};
let cameras = {};
let renderers = {};
let controls = {};
let objects = {};

/**
 * Creates the dorm room scene with furniture based on the DSL layout
 * @param {THREE.Scene} scene - The Three.js scene to add objects to
 * @param {Object} roomData - The room data from the DSL
 * @param {Array} furnitureData - The furniture data from the DSL
 */
function createDormRoom(scene, roomData, furnitureData) {
  // Create utilities
  const utils = createDormRoomUtils();
  
  // Set up room dimensions
  const roomWidth = roomData.width / 100; // Convert to meters
  const roomLength = roomData.length / 100;
  const roomHeight = roomData.height / 100;

  console.log('Creating dorm room with dimensions:', { roomWidth, roomLength, roomHeight });
  console.log('Furniture data:', furnitureData);
  
  // Create room
  const room = utils.createRoom(roomData.name, roomWidth, roomLength, roomHeight, roomData.type);
  scene.add(room);

  // Process furniture
  furnitureData.forEach(item => {
    // Check if item has required properties
    if (!item || !item.item) {
      console.warn('Invalid furniture item:', item);
      return; // Skip this item
    }
    
    console.log(`Processing furniture item: ${item.item}`);
    
    // Get position and convert to meters
    let x = 0, z = 0, y = 0;
    
    // Check if position exists and is an array with at least 2 elements
    if (item.position && Array.isArray(item.position) && item.position.length >= 2) {
      x = item.position[0] / 100;
      z = item.position[1] / 100;
      console.log(`Position from array: [${item.position[0]}, ${item.position[1]}] -> [${x}, ${z}] meters`);
    } else if (item.position && typeof item.position === 'string') {
      // Try to parse position string if it's not already an array
      console.log(`Position as string: "${item.position}"`);
      const posParts = item.position.split(/[,\s]+/).filter(p => p.trim() !== '');
      console.log(`Split position parts:`, posParts);
      
      if (posParts.length >= 2) {
        x = parseFloat(posParts[0]) / 100;
        z = parseFloat(posParts[1]) / 100;
        console.log(`Parsed position from string: [${x}, ${z}] meters`);
      } else {
        console.warn(`Invalid position format for item ${item.item}: ${item.position}`);
      }
    } else {
      console.warn(`Missing or invalid position for item ${item.item}:`, item.position);
    }
    
    // Get rotation in radians
    const rotation = item.rotation ? item.rotation * (Math.PI / 180) : 0;
    console.log(`Rotation: ${item.rotation} degrees -> ${rotation} radians`);
    
    // Check if item should be placed on top of another item
    if (item.ontop) {
      console.log(`Item ${item.item} should be placed on top of ${item.ontop}`);
      // Find the base item
      const baseItem = furnitureData.find(i => i.item === item.ontop);
      if (baseItem && baseItem.position && Array.isArray(baseItem.position) && baseItem.position.length >= 2) {
        // Get base position
        const baseX = baseItem.position[0] / 100;
        const baseZ = baseItem.position[1] / 100;
        console.log(`Base item position: [${baseX}, ${baseZ}] meters`);
        
        // Add relative position to base position
        x = baseX + x / 100;
        z = baseZ + z / 100;
        console.log(`Adjusted position for item on top: [${x}, ${z}] meters`);
        
        // Set Y position based on furniture type
        switch(item.ontop) {
          case 'desk':
            y = 0.75;
            break;
          case 'dresser':
            y = 0.80;
            break;
          case 'bookshelf':
            // Variable height depending on which shelf
            y = 0.40;
            break;
          case 'minifridge':
            y = 0.85;
            break;
          default:
            y = 0;
        }
        console.log(`Y position for item on top: ${y} meters`);
      } else {
        console.warn(`Base item ${item.ontop} not found or has invalid position for item ${item.item}`);
      }
    }
    
    // Create furniture based on type
    let furniture;
    switch(item.item) {
      case 'bed':
        furniture = utils.createBed();
        break;
      case 'desk':
        furniture = utils.createDesk();
        break;
      case 'chair':
        furniture = utils.createChair();
        break;
      case 'dresser':
        furniture = utils.createDresser();
        break;
      case 'bookshelf':
        furniture = utils.createBookshelf();
        break;
      case 'minifridge':
        furniture = utils.createMinifridge();
        break;
      case 'microwave':
        furniture = utils.createMicrowave();
        break;
      case 'lamp':
        furniture = utils.createLamp();
        break;
      case 'storage_bin':
        furniture = utils.createStorageBin();
        break;
      case 'bulletin_board':
        furniture = utils.createBulletinBoard();
        break;
      default:
        console.warn(`Unknown furniture type: ${item.item}`);
        return; // Skip this item
    }
    
    // Position and rotate furniture
    if (furniture) {
      console.log(`Setting position for ${item.item} to [${x}, ${y}, ${z}]`);
      furniture.position.set(x, y, z);
      furniture.rotation.y = rotation;
      scene.add(furniture);
      console.log(`Added ${item.item} to scene`);
    }
  });

  return scene;
}

/**
 * Creates utility functions for building dorm room furniture
 * @returns {Object} Object containing furniture creation functions
 */
function createDormRoomUtils() {
  return {
    // Create a room with walls, floor and ceiling
    createRoom: function(name, width, length, height, type) {
      const room = new THREE.Group();
      
      // Floor
      const floorGeometry = new THREE.PlaneGeometry(width, length);
      const floorMaterial = new THREE.MeshStandardMaterial({ 
        color: 0xeeeeee,
        roughness: 0.8,
        metalness: 0.2
      });
      const floor = new THREE.Mesh(floorGeometry, floorMaterial);
      floor.rotation.x = -Math.PI / 2;
      floor.position.set(width/2, 0, length/2);
      floor.receiveShadow = true;
      room.add(floor);
      
      // Walls
      const wallMaterial = new THREE.MeshStandardMaterial({ 
        color: 0xfafafa,
        roughness: 0.9,
        metalness: 0.1
      });
      
      // Back wall
      const backWallGeometry = new THREE.PlaneGeometry(width, height);
      const backWall = new THREE.Mesh(backWallGeometry, wallMaterial);
      backWall.position.set(width/2, height/2, 0);
      backWall.receiveShadow = true;
      room.add(backWall);
      
      // Right wall
      const rightWallGeometry = new THREE.PlaneGeometry(length, height);
      const rightWall = new THREE.Mesh(rightWallGeometry, wallMaterial);
      rightWall.rotation.y = -Math.PI / 2;
      rightWall.position.set(width, height/2, length/2);
      rightWall.receiveShadow = true;
      room.add(rightWall);
      
      // Left wall
      const leftWallGeometry = new THREE.PlaneGeometry(length, height);
      const leftWall = new THREE.Mesh(leftWallGeometry, wallMaterial);
      leftWall.rotation.y = Math.PI / 2;
      leftWall.position.set(0, height/2, length/2);
      leftWall.receiveShadow = true;
      room.add(leftWall);
      
      return room;
    },
    
    // Create a bed
    createBed: function() {
      const group = new THREE.Group();
      
      // Bed frame
      const frameGeometry = new THREE.BoxGeometry(0.9, 0.2, 2.0);
      const frameMaterial = new THREE.MeshPhongMaterial({ 
        color: 0x8b4513, // Brown
        flatShading: true
      });
      const frame = new THREE.Mesh(frameGeometry, frameMaterial);
      frame.position.y = 0.1;
      frame.castShadow = true;
      frame.receiveShadow = true;
      group.add(frame);
      
      // Mattress
      const mattressGeometry = new THREE.BoxGeometry(0.85, 0.15, 1.95);
      const mattressMaterial = new THREE.MeshPhongMaterial({ 
        color: 0xffffff, // White
        flatShading: true
      });
      const mattress = new THREE.Mesh(mattressGeometry, mattressMaterial);
      mattress.position.y = 0.275;
      mattress.castShadow = true;
      group.add(mattress);
      
      // Pillow
      const pillowGeometry = new THREE.BoxGeometry(0.7, 0.1, 0.4);
      const pillowMaterial = new THREE.MeshPhongMaterial({ 
        color: 0xf0f0f0, // Light white
        flatShading: true
      });
      const pillow = new THREE.Mesh(pillowGeometry, pillowMaterial);
      pillow.position.set(0, 0.35, -0.7);
      pillow.castShadow = true;
      group.add(pillow);
      
      // Blanket
      const blanketGeometry = new THREE.BoxGeometry(0.85, 0.05, 1.4);
      const blanketMaterial = new THREE.MeshPhongMaterial({ 
        color: 0x4169e1, // Royal blue
        flatShading: true
      });
      const blanket = new THREE.Mesh(blanketGeometry, blanketMaterial);
      blanket.position.set(0, 0.375, 0.3);
      blanket.castShadow = true;
      group.add(blanket);
      
      return group;
    },
    
    // Create a desk
    createDesk: function() {
      const group = new THREE.Group();
      
      // Desk top
      const topGeometry = new THREE.BoxGeometry(1.2, 0.05, 0.6);
      const topMaterial = new THREE.MeshPhongMaterial({ 
        color: 0xd2b48c, // Tan
        flatShading: true
      });
      const top = new THREE.Mesh(topGeometry, topMaterial);
      top.position.y = 0.725;
      top.castShadow = true;
      top.receiveShadow = true;
      group.add(top);
      
      // Legs
      const legGeometry = new THREE.BoxGeometry(0.05, 0.7, 0.05);
      const legMaterial = new THREE.MeshPhongMaterial({ 
        color: 0xd2b48c, // Tan
        flatShading: true
      });
      
      // Add four legs
      const legs = [
        { x: -0.55, z: -0.25 },
        { x: 0.55, z: -0.25 },
        { x: -0.55, z: 0.25 },
        { x: 0.55, z: 0.25 }
      ];
      
      legs.forEach(pos => {
        const leg = new THREE.Mesh(legGeometry, legMaterial);
        leg.position.set(pos.x, 0.35, pos.z);
        leg.castShadow = true;
        leg.receiveShadow = true;
        group.add(leg);
      });
      
      // Drawer
      const drawerGeometry = new THREE.BoxGeometry(0.4, 0.15, 0.5);
      const drawerMaterial = new THREE.MeshPhongMaterial({ 
        color: 0xc19a6b, // Darker tan
        flatShading: true
      });
      const drawer = new THREE.Mesh(drawerGeometry, drawerMaterial);
      drawer.position.set(0.3, 0.625, 0);
      drawer.castShadow = true;
      group.add(drawer);
      
      // Handle
      const handleGeometry = new THREE.BoxGeometry(0.2, 0.02, 0.02);
      const handleMaterial = new THREE.MeshPhongMaterial({ 
        color: 0x808080, // Gray
        flatShading: true
      });
      const handle = new THREE.Mesh(handleGeometry, handleMaterial);
      handle.position.set(0.3, 0.625, -0.26);
      drawer.add(handle);
      
      return group;
    },
    
    // Create a chair
    createChair: function() {
      const group = new THREE.Group();
      
      // Seat
      const seatGeometry = new THREE.BoxGeometry(0.4, 0.05, 0.4);
      const seatMaterial = new THREE.MeshPhongMaterial({ 
        color: 0x8b4513, // Brown
        flatShading: true
      });
      const seat = new THREE.Mesh(seatGeometry, seatMaterial);
      seat.position.y = 0.45;
      seat.castShadow = true;
      group.add(seat);
      
      // Backrest
      const backrestGeometry = new THREE.BoxGeometry(0.4, 0.4, 0.05);
      const backrestMaterial = new THREE.MeshPhongMaterial({ 
        color: 0x8b4513, // Brown
        flatShading: true
      });
      const backrest = new THREE.Mesh(backrestGeometry, backrestMaterial);
      backrest.position.set(0, 0.675, -0.175);
      backrest.castShadow = true;
      group.add(backrest);
      
      // Legs
      const legGeometry = new THREE.CylinderGeometry(0.02, 0.02, 0.45, 8);
      const legMaterial = new THREE.MeshPhongMaterial({ 
        color: 0x696969, // Dark gray
        flatShading: true
      });
      
      // Add four legs
      const legs = [
        { x: -0.15, z: -0.15 },
        { x: 0.15, z: -0.15 },
        { x: -0.15, z: 0.15 },
        { x: 0.15, z: 0.15 }
      ];
      
      legs.forEach(pos => {
        const leg = new THREE.Mesh(legGeometry, legMaterial);
        leg.position.set(pos.x, 0.225, pos.z);
        leg.castShadow = true;
        group.add(leg);
      });
      
      return group;
    },
    
    // Create a dresser
    createDresser: function() {
      const group = new THREE.Group();
      
      // Body
      const bodyGeometry = new THREE.BoxGeometry(0.6, 0.8, 0.4);
      const bodyMaterial = new THREE.MeshPhongMaterial({ 
        color: 0xd2b48c, // Tan
        flatShading: true
      });
      const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
      body.position.y = 0.4;
      body.castShadow = true;
      body.receiveShadow = true;
      group.add(body);
      
      // Drawers
      const drawerGeometry = new THREE.BoxGeometry(0.56, 0.15, 0.01);
      const drawerMaterial = new THREE.MeshPhongMaterial({ 
        color: 0xc19a6b, // Darker tan
        flatShading: true
      });
      
      // Create 4 drawers
      for (let i = 0; i < 4; i++) {
        const drawer = new THREE.Mesh(drawerGeometry, drawerMaterial);
        // Center the drawers vertically and horizontally
        drawer.position.set(0, -0.3 + i*0.2, 0.2);
        body.add(drawer);
        
        // Drawer handle
        const handleGeometry = new THREE.CylinderGeometry(0.02, 0.02, 0.15, 8);
        const handleMaterial = new THREE.MeshPhongMaterial({ 
          color: 0x808080, // Gray
          flatShading: true
        });
        const handle = new THREE.Mesh(handleGeometry, handleMaterial);
        handle.rotation.x = Math.PI / 2;
        handle.position.set(0, 0, -0.03);
        drawer.add(handle);
      }
      
      return group;
    },
    
    // Create a bookshelf
    createBookshelf: function() {
      const group = new THREE.Group();
      
      // Body
      const bodyGeometry = new THREE.BoxGeometry(0.8, 1.8, 0.02);
      const bodyMaterial = new THREE.MeshPhongMaterial({ 
        color: 0x8b4513, // Brown
        flatShading: true
      });
      const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
      body.position.y = 0.9;
      body.castShadow = true;
      body.receiveShadow = true;
      group.add(body);
      
      // Shelves
      const shelfGeometry = new THREE.BoxGeometry(0.76, 0.02, 0.28);
      const shelfMaterial = new THREE.MeshPhongMaterial({ 
        color: 0x8b4513, // Brown
        flatShading: true
      });
      
      // Create 5 shelves
      for (let i = 0; i < 5; i++) {
        const shelf = new THREE.Mesh(shelfGeometry, shelfMaterial);
        shelf.position.set(0, -0.7 + i*0.4, 0);
        body.add(shelf);
      }
      
      // Add some books for visual interest
      const colors = [0xff0000, 0x00ff00, 0x0000ff, 0xffff00, 0xff00ff];
      
      for (let shelf = 0; shelf < 4; shelf++) {
        let offset = 0;
        
        // Add a random number of books to each shelf
        for (let i = 0; i < 5 + Math.floor(Math.random() * 3); i++) {
          const width = 0.05 + Math.random() * 0.1;
          const height = 0.2 + Math.random() * 0.1;
          
          const bookGeometry = new THREE.BoxGeometry(width, height, 0.2);
          const bookMaterial = new THREE.MeshPhongMaterial({ 
            color: colors[Math.floor(Math.random() * colors.length)],
            flatShading: true
          });
          
          const book = new THREE.Mesh(bookGeometry, bookMaterial);
          book.position.set(offset - 0.3, -0.5 + shelf*0.4, 0);
          offset += width + 0.02;
          body.add(book);
        }
      }
      
      return group;
    },
    
    // Create a minifridge
    createMinifridge: function() {
      const group = new THREE.Group();
      
      // Body
      const bodyGeometry = new THREE.BoxGeometry(0.5, 0.85, 0.5);
      const bodyMaterial = new THREE.MeshPhongMaterial({ 
        color: 0xffffff, // White
        flatShading: true
      });
      const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
      body.position.y = 0.425;
      body.castShadow = true;
      body.receiveShadow = true;
      group.add(body);
      
      // Door edge
      const doorEdgeGeometry = new THREE.BoxGeometry(0.48, 0.83, 0.01);
      const doorEdgeMaterial = new THREE.MeshPhongMaterial({ 
        color: 0xe0e0e0, // Light gray
        flatShading: true
      });
      const doorEdge = new THREE.Mesh(doorEdgeGeometry, doorEdgeMaterial);
      doorEdge.position.set(0, 0, 0.255);
      body.add(doorEdge);
      
      // Handle
      const handleGeometry = new THREE.BoxGeometry(0.03, 0.2, 0.02);
      const handleMaterial = new THREE.MeshPhongMaterial({ 
        color: 0x808080, // Gray
        flatShading: true
      });
      const handle = new THREE.Mesh(handleGeometry, handleMaterial);
      handle.position.set(0.2, 0.1, 0.01);
      doorEdge.add(handle);
      
      // Logo
      const logoGeometry = new THREE.PlaneGeometry(0.1, 0.1);
      const logoMaterial = new THREE.MeshBasicMaterial({ 
        color: 0x0000ff, // Blue
      });
      const logo = new THREE.Mesh(logoGeometry, logoMaterial);
      logo.position.set(0, 0.3, 0.01);
      doorEdge.add(logo);
      
      return group;
    },
    
    // Create a microwave
    createMicrowave: function() {
      const group = new THREE.Group();
      
      // Body
      const bodyGeometry = new THREE.BoxGeometry(0.4, 0.25, 0.3);
      const bodyMaterial = new THREE.MeshPhongMaterial({ 
        color: 0x303030, // Dark gray
        flatShading: true
      });
      const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
      body.position.y = 0.125;
      body.castShadow = true;
      group.add(body);
      
      // Door
      const doorGeometry = new THREE.PlaneGeometry(0.25, 0.2);
      const doorMaterial = new THREE.MeshPhongMaterial({ 
        color: 0x000000, // Black
        transparent: true,
        opacity: 0.7,
        flatShading: true
      });
      const door = new THREE.Mesh(doorGeometry, doorMaterial);
      door.position.set(-0.075, 0, 0.151);
      body.add(door);
      
      // Control panel
      const panelGeometry = new THREE.PlaneGeometry(0.1, 0.2);
      const panelMaterial = new THREE.MeshPhongMaterial({ 
        color: 0x202020, // Very dark gray
        flatShading: true
      });
      const panel = new THREE.Mesh(panelGeometry, panelMaterial);
      panel.position.set(0.15, 0, 0.151);
      body.add(panel);
      
      // Buttons
      for (let i = 0; i < 9; i++) {
        const row = Math.floor(i / 3);
        const col = i % 3;
        
        const buttonGeometry = new THREE.PlaneGeometry(0.02, 0.02);
        const buttonMaterial = new THREE.MeshBasicMaterial({ 
          color: 0xffffff, // White
        });
        const button = new THREE.Mesh(buttonGeometry, buttonMaterial);
        button.position.set(0.13 + col*0.03, 0.06 - row*0.03, 0.152);
        body.add(button);
      }
      
      return group;
    },
    
    // Create a lamp
    createLamp: function() {
      const group = new THREE.Group();
      
      // Base
      const baseGeometry = new THREE.CylinderGeometry(0.1, 0.12, 0.05, 16);
      const baseMaterial = new THREE.MeshPhongMaterial({ 
        color: 0xc0c0c0, // Silver
        flatShading: true
      });
      const base = new THREE.Mesh(baseGeometry, baseMaterial);
      base.position.y = 0.025;
      base.castShadow = true;
      group.add(base);
      
      // Stem
      const stemGeometry = new THREE.CylinderGeometry(0.02, 0.02, 0.35, 8);
      const stemMaterial = new THREE.MeshPhongMaterial({ 
        color: 0xc0c0c0, // Silver
        flatShading: true
      });
      const stem = new THREE.Mesh(stemGeometry, stemMaterial);
      stem.position.y = 0.225;
      stem.castShadow = true;
      group.add(stem);
      
      // Shade
      const shadeGeometry = new THREE.ConeGeometry(0.15, 0.2, 16, 1, true);
      const shadeMaterial = new THREE.MeshPhongMaterial({ 
        color: 0xfffaf0, // Cream
        flatShading: true,
        side: THREE.DoubleSide
      });
      const shade = new THREE.Mesh(shadeGeometry, shadeMaterial);
      shade.position.y = 0.4;
      shade.rotation.x = 0; // Changed from Math.PI to 0 to flip the cone
      shade.castShadow = true;
      group.add(shade);
      
      // Light (point light)
      const light = new THREE.PointLight(0xffffcc, 0.5, 1);
      light.position.set(0, 0.35, 0);
      light.castShadow = true;
      group.add(light);
      
      return group;
    },
    
    // Create a storage bin
    createStorageBin: function() {
      const group = new THREE.Group();
      
      // Box
      const boxGeometry = new THREE.BoxGeometry(0.6, 0.3, 0.4);
      const boxMaterial = new THREE.MeshPhongMaterial({ 
        color: 0x6495ed, // Cornflower blue
        flatShading: true
      });
      const box = new THREE.Mesh(boxGeometry, boxMaterial);
      box.position.y = 0.15;
      box.castShadow = true;
      group.add(box);
      
      // Lid
      const lidGeometry = new THREE.BoxGeometry(0.6, 0.05, 0.4);
      const lidMaterial = new THREE.MeshPhongMaterial({ 
        color: 0x4682b4, // Steel blue (slightly darker)
        flatShading: true
      });
      const lid = new THREE.Mesh(lidGeometry, lidMaterial);
      lid.position.y = 0.325;
      lid.castShadow = true;
      group.add(lid);
      
      // Handle
      const handleGeometry = new THREE.BoxGeometry(0.2, 0.03, 0.05);
      const handleMaterial = new THREE.MeshPhongMaterial({ 
        color: 0x4682b4, // Steel blue
        flatShading: true
      });
      const handle = new THREE.Mesh(handleGeometry, handleMaterial);
      handle.position.y = 0.03;
      lid.add(handle);
      
      return group;
    },
    
    // Create a bulletin board
    createBulletinBoard: function() {
      const group = new THREE.Group();
      
      // Frame
      const frameGeometry = new THREE.BoxGeometry(0.8, 0.6, 0.02);
      const frameMaterial = new THREE.MeshPhongMaterial({ 
        color: 0x8b4513, // Brown
        flatShading: true
      });
      const frame = new THREE.Mesh(frameGeometry, frameMaterial);
      frame.position.y = 1.5;
      frame.castShadow = true;
      group.add(frame);
      
      // Cork background
      const corkGeometry = new THREE.PlaneGeometry(0.76, 0.56);
      const corkMaterial = new THREE.MeshPhongMaterial({ 
        color: 0xdeb887, // Burlywood
        flatShading: true
      });
      const cork = new THREE.Mesh(corkGeometry, corkMaterial);
      cork.position.z = 0.011;
      frame.add(cork);
      
      // Add some notes (simple colored squares)
      const colors = [0xffffff, 0xffff99, 0x99ff99, 0x9999ff, 0xff9999];
      
      for (let i = 0; i < 6; i++) {
        const noteSize = 0.1 + Math.random() * 0.05;
        
        const noteGeometry = new THREE.PlaneGeometry(noteSize, noteSize);
        const noteMaterial = new THREE.MeshBasicMaterial({ 
          color: colors[Math.floor(Math.random() * colors.length)],
        });
        const note = new THREE.Mesh(noteGeometry, noteMaterial);
        
        // Random position within the cork board
        const x = (Math.random() * 0.6 - 0.3);
        const y = (Math.random() * 0.4 - 0.2);
        
        note.position.set(x, y, 0.012);
        
        // Random rotation
        note.rotation.z = (Math.random() * 0.4) - 0.2;
        
        frame.add(note);
      }
      
      // Add some pins
      for (let i = 0; i < 8; i++) {
        const pinGeometry = new THREE.SphereGeometry(0.01, 8, 8);
        const pinMaterial = new THREE.MeshPhongMaterial({ 
          color: Math.random() > 0.5 ? 0xff0000 : 0x0000ff, // Red or blue
          flatShading: true
        });
        const pin = new THREE.Mesh(pinGeometry, pinMaterial);
        
        // Random position within the cork board
        const x = (Math.random() * 0.7 - 0.35);
        const y = (Math.random() * 0.5 - 0.25);
        
        pin.position.set(x, y, 0.015);
        frame.add(pin);
      }
      
      return group;
    }
  };
}

/**
 * Parses the DormRoomDSL and generates Three.js code
 * @param {string} dslContent - The DSL content as a string
 * @returns {Object} Object with room and furniture data
 */
function parseDormRoomDSL(dslString) {
  // Trim the input and split by lines
  const lines = dslString.trim().split('\n').map(line => line.trim());
  
  // Initialize result object
  const result = {
    room: {
      name: "Default Room",
      width: 0,
      length: 0,
      height: 0,
      type: "single"
    },
    furniture: []
  };
  
  // Current parsing state
  let currentSection = null;
  let currentItem = null;
  let indentLevel = 0;
  
  // Helper to get indent level of a line
  function getIndent(line) {
    const match = line.match(/^(\s*)/);
    return match ? match[1].length : 0;
  }
  
  // Process each line
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line === '') continue; // Skip empty lines
    
    // Determine current section based on line content
    if (line.startsWith('room:')) {
      currentSection = 'room';
      continue;
    } else if (line.startsWith('layout:')) {
      currentSection = 'layout';
      continue;
    }
    
    // Process room section
    if (currentSection === 'room') {
      const colonIndex = line.indexOf(':');
      if (colonIndex > 0) {
        const key = line.substring(0, colonIndex).trim();
        let value = line.substring(colonIndex + 1).trim();
        
        // Remove quotes from string values
        if (value.startsWith('"') && value.endsWith('"')) {
          value = value.slice(1, -1);
        }
        
        // Convert numeric values
        if (!isNaN(value) && value !== '') {
          value = Number(value);
        }
        
        // Store the value in the result object
        if (key !== 'unit') { // Skip 'unit' property as it's not in the output format
          result.room[key] = value;
        }
      }
    }
    
    // Process layout section
    else if (currentSection === 'layout') {
      // Check for a new item
      if (line.startsWith('-')) {
        // Create a new item and push it to the furniture array
        currentItem = {};
        result.furniture.push(currentItem);
      }
      
      // Process item properties
      const colonIndex = line.indexOf(':');
      if (colonIndex > 0) {
        const key = line.substring(line.indexOf('item:') !== -1 ? line.indexOf('item:') : 0, colonIndex).trim();
        let value = line.substring(colonIndex + 1).trim();
        
        // Handle different property types
        if (key === 'item') {
          currentItem.item = value;
        } else if (key === 'position') {
          // Parse position array
          value = value.replace('[', '').replace(']', '');
          const positions = value.split(',').map(pos => Number(pos.trim()));
          currentItem.position = positions;
        } else if (key === 'rotation') {
          currentItem.rotation = Number(value);
        } else if (key === 'ontop') {
          currentItem.ontop = value;
        }
      }
    }
  }
  
  // Return the structured result
  return result;
}

// Fetch JavaScript files from the server
async function fetchJsFiles() {
    try {
        const response = await fetch('/api/js');
        jsFiles = await response.json();
        
        // Check if each JS file has a corresponding DSL file
        for (let i = 0; i < jsFiles.length; i++) {
            const jsName = jsFiles[i].name;
            const dslName = jsName.replace('.js', '.dsl');
            
            try {
                // Try to fetch the corresponding DSL file
                const dslResponse = await fetch(`/api/dsl/${dslName}`);
                if (dslResponse.ok) {
                    const dslContent = await dslResponse.text();
                    jsFiles[i].dslContent = dslContent;
                }
            } catch (error) {
                console.warn(`No DSL file found for ${jsName}: ${error.message}`);
            }
        }
        
        renderJsFiles();
    } catch (error) {
        showStatus('Error loading JavaScript files: ' + error.message, 'error');
    }
}

// Render JavaScript files in the grid
function renderJsFiles() {
    const grid = document.getElementById('threejsGrid');
    grid.innerHTML = '';
    
    jsFiles.forEach((jsData, index) => {
        const jsName = jsData.name;
        const jsContent = jsData.content;
        
        const item = document.createElement('div');
        item.className = 'threejs-item';
        if (selectedJs === jsName) {
            item.classList.add('selected');
            selectedIndex = index;
        }
        
        // Add feedback badge if there's feedback
        const hasFeedback = feedbackData[jsName] && feedbackData[jsName].length > 0;
        
        item.innerHTML = `
            <div class="js-number">${index + 1}</div>
            ${hasFeedback ? `<div class="feedback-badge">${feedbackData[jsName].length}</div>` : ''}
            <div class="threejs-preview" id="preview-${index}"></div>
        `;
        
        item.addEventListener('click', () => {
            selectJs(jsName);
        });

        item.addEventListener('dblclick', () => {
            saveSelected();
        });
        
        grid.appendChild(item);
        
        // Default DSL content for dorm room
        const defaultDslContent = `
room:
  name: "Jones Hall 101"
  width: 300
  length: 250
  height: 240
  unit: cm
  type: single
    
layout:
  - item: bed
    position: [30, 30]
    rotation: 0
    
  - item: desk
    position: [30, 150]
    rotation: 0
    
  - item: chair
    position: [30, 200]
    rotation: 180
    
  - item: dresser
    position: [200, 30]
    rotation: 270
    
  - item: bookshelf
    position: [200, 150]
    rotation: 270
    
  - item: minifridge
    position: [200, 220]
    rotation: 270
    
  - item: microwave
    ontop: minifridge
    position: [10, 10]
    
  - item: lamp
    ontop: desk
    position: [50, 20]
    
  - item: storage_bin
    position: [30, 100]
    rotation: 0
    
  - item: bulletin_board
    position: [30, 240]
    rotation: 0
`;
        
        // Use DSL content from server if available, otherwise use default
        const dslContent = jsData.dslContent || defaultDslContent;
        
        // Initialize Three.js scene for this preview with DSL content
        initThreeJsScene(index, jsContent, dslContent);
    });
}

// Initialize Three.js scene for a preview
// Initialize Three.js scene for a dorm room preview
async function initThreeJsScene(index, jsContent, dslContent) {
    const container = document.getElementById(`preview-${index}`);
    if (!container) return;

    const width = container.clientWidth;
    const height = container.clientHeight;
    
    // Create scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);
    scenes[index] = scene;
    
    // Create camera
    const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 1000);
    cameras[index] = camera;
    camera.position.set(5, 5, 5);
    camera.lookAt(0, 0, 0);
    
    // Create renderer
    const renderer = new THREE.WebGLRenderer({ 
        antialias: true,
        alpha: true
    });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(width, height);
    renderer.shadowMap.enabled = true;
    renderers[index] = renderer;
    container.appendChild(renderer.domElement);
    
    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 5, 5);
    directionalLight.castShadow = true;
    scene.add(directionalLight);

    const fillLight = new THREE.DirectionalLight(0xffffff, 0.4);
    fillLight.position.set(-5, 0, -5);
    scene.add(fillLight);
    
    // Add orbit controls
    const orbitControls = new THREE.OrbitControls(camera, renderer.domElement);
    orbitControls.enableDamping = false;
    orbitControls.enableZoom = true;
    orbitControls.enablePan = true;
    orbitControls.autoRotate = true;
    orbitControls.autoRotateSpeed = 1.3;
    controls[index] = orbitControls;
    
    try {
        // Create a blob URL from the JavaScript content
        const blob = new Blob([jsContent], { type: 'application/javascript' });
        const blobUrl = URL.createObjectURL(blob);
        
        // Load the script
        const script = document.createElement('script');
        script.src = blobUrl;
        
        // Wait for script to load
        await new Promise((resolve, reject) => {
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
        
        // Clean up
        URL.revokeObjectURL(blobUrl);
        document.head.removeChild(script);
        
        // Parse the DSL content if provided
        let dslData = null;
        if (dslContent) {
            dslData = parseDormRoomDSL(dslContent);
            if (!dslData) {
                console.warn('Failed to parse DSL content, using default scene');
                // Create default DSL data
                dslData = {
                    room: {
                        name: "Default Room",
                        width: 300,
                        length: 250,
                        height: 240,
                        type: "single"
                    },
                    furniture: [
                        { item: 'bed', position: [30, 30], rotation: 0 },
                        { item: 'desk', position: [30, 150], rotation: 0 }
                    ]
                };
            }
        } else {
            console.warn('No DSL content provided, using default scene');
            // Create default DSL data
            dslData = {
                room: {
                    name: "Default Room",
                    width: 300,
                    length: 250,
                    height: 240,
                    type: "single"
                },
                furniture: [
                    { item: 'bed', position: [30, 30], rotation: 0 },
                    { item: 'desk', position: [30, 150], rotation: 0 }
                ]
            };
        }
        
        // Check if the required functions are available
        if (typeof createDormRoom === 'function' && typeof createDormRoomUtils === 'function') {
            // Create a dorm room with the parsed DSL data
            const roomObj = createDormRoom(scene, dslData.room, dslData.furniture);
            objects[index] = roomObj || scene;
            
            // Create a bounding box from all objects in the scene
            const box = new THREE.Box3();
            scene.traverse(object => {
                if (object.isMesh) {
                    box.expandByObject(object);
                }
            });
            
            const center = box.getCenter(new THREE.Vector3());
            const size = box.getSize(new THREE.Vector3());
            
            // Position camera to better view the scene
            const maxDim = Math.max(size.x, size.y, size.z);
            const distance = maxDim * 2;
            
            // Position camera to see the room from a good viewpoint
            camera.position.set(
                center.x + distance * 0.6, 
                center.y + distance * 0.5, 
                center.z + distance * 0.6
            );
            camera.lookAt(center);
            
            // Update controls to target the center
            controls[index].target.set(center.x, center.y, center.z);
            controls[index].update();
        } else {
            throw new Error('Required functions not found in the JavaScript code');
        }
    } catch (error) {
        console.error('Error creating dorm room:', error);
        showStatus('Error creating dorm room: ' + error.message, 'error');
    }
    
    // Animate
    function animate() {
        requestAnimationFrame(animate);
        controls[index].update();
        renderer.render(scene, camera);
    }
    animate();
}

// Select a JavaScript file
async function selectJs(js) {
    try {
        const response = await fetch('/api/select', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ js })
        });
        
        if (response.ok) {
            selectedJs = js;
            renderJsFiles();
            loadFeedback(js);
        } else {
            showStatus('Error selecting JavaScript file', 'error');
        }
    } catch (error) {
        showStatus('Error selecting JavaScript file: ' + error.message, 'error');
    }
}

// Load feedback for a specific JavaScript file
async function loadFeedback(js) {
    try {
        const response = await fetch(`/api/feedback/${js}`);
        const data = await response.json();
        
        feedbackData[js] = data.feedback;
        renderFeedbackList();
    } catch (error) {
        console.error('Error loading feedback:', error);
    }
}

// Render feedback list
function renderFeedbackList() {
    const list = document.getElementById('feedbackList');
    list.innerHTML = '';
    
    if (!selectedJs || !feedbackData[selectedJs] || feedbackData[selectedJs].length === 0) {
        list.innerHTML = '<div class="feedback-empty-state">No feedback yet</div>';
        return;
    }
    
    feedbackData[selectedJs].forEach((feedback, index) => {
        const feedbackItem = document.createElement('div');
        feedbackItem.className = 'feedback-item';
        feedbackItem.textContent = feedback;
        list.appendChild(feedbackItem);
    });
}

// Save feedback for selected JavaScript file
async function saveFeedback() {
    const feedback = document.getElementById('feedbackInput').value.trim();
    
    if (!feedback) {
        showStatus('Please enter feedback', 'error');
        return;
    }
    
    if (!selectedJs) {
        showStatus('Please select an object first', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ js: selectedJs, feedback })
        });
        
        if (response.ok) {
            showStatus(`Feedback saved for ${selectedJs}`, 'success');
            document.getElementById('feedbackInput').value = '';
            
            // Reload feedback for the selected JavaScript file
            await loadFeedback(selectedJs);
        } else {
            showStatus('Error saving feedback', 'error');
        }
    } catch (error) {
        showStatus('Error saving feedback: ' + error.message, 'error');
    }
}

// Save selected JavaScript file
async function saveSelected() {
    if (!selectedJs) {
        showStatus('No object selected', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/save-selected', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        if (response.ok) {
            const data = await response.json();
            showStatus(`Object ${selectedJs} saved to ${data.path}`, 'success');
        } else {
            showStatus('Error saving object', 'error');
        }
    } catch (error) {
        showStatus('Error saving object: ' + error.message, 'error');
    }
}

// Close the viewer
async function closeViewer() {
    if (isClosing) return;
    
    isClosing = true;
    try {
        const response = await fetch('/api/close', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            window.close();
        } else {
            showStatus('Error closing viewer', 'error');
            isClosing = false;
        }
    } catch (error) {
        showStatus('Error closing viewer: ' + error.message, 'error');
        isClosing = false;
    }
}

// Show status message
function showStatus(message, type = 'info') {
    const status = document.getElementById('status');
    status.textContent = message;
    status.className = `status ${type}`;
    status.style.display = 'block';
    
    setTimeout(() => {
        status.style.display = 'none';
    }, 3000);
}

// Navigate to previous JavaScript file
function navigatePrevious() {
    if (jsFiles.length === 0) return;
    
    let newIndex = selectedIndex - 1;
    if (newIndex < 0) newIndex = jsFiles.length - 1;
    
    selectJs(jsFiles[newIndex].name);
}

// Navigate to next JavaScript file
function navigateNext() {
    if (jsFiles.length === 0) return;
    
    let newIndex = selectedIndex + 1;
    if (newIndex >= jsFiles.length) newIndex = 0;
    
    selectJs(jsFiles[newIndex].name);
}

// Handle keyboard shortcuts
function handleKeyDown(e) {
    // If user is typing in the feedback input, don't handle navigation keys
    if (e.target.id === 'feedbackInput') {
        if (e.key === 'Enter') {
            e.preventDefault();
            saveFeedback();
        }
        return;
    }
    
    switch (e.key) {
        case 'ArrowLeft':
            e.preventDefault();
            navigatePrevious();
            break;
        case 'ArrowRight':
            e.preventDefault();
            navigateNext();
            break;
        case 'Enter':
            e.preventDefault();
            if (selectedJs) {
                document.getElementById('feedbackInput').focus();
            }
            break;
        case 'Escape':
            e.preventDefault();
            closeViewer();
            break;
        case 's':
        case 'S':
            e.preventDefault();
            saveSelected();
            break;
    }
}

// Handle window resize
function handleResize() {
    jsFiles.forEach((_, index) => {
        const container = document.getElementById(`preview-${index}`);
        if (container && renderers[index] && cameras[index]) {
            const width = container.clientWidth;
            const height = container.clientHeight;
            
            cameras[index].aspect = width / height;
            cameras[index].updateProjectionMatrix();
            
            renderers[index].setSize(width, height, true);
        }
    });
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    fetchJsFiles();
    document.addEventListener('keydown', handleKeyDown);
    window.addEventListener('resize', handleResize);
    
    document.getElementById('saveFeedbackBtn').addEventListener('click', saveFeedback);
}); 