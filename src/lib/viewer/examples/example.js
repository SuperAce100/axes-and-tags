// Create a basic room with walls, floor and ceiling
function createRoom(name, width, length, height, type) {
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
  
  // Add room label
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');
  canvas.width = 256;
  canvas.height = 64;
  context.fillStyle = '#ffffff';
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.font = '24px Arial';
  context.fillStyle = '#000000';
  context.textAlign = 'center';
  context.textBaseline = 'middle';
  context.fillText(name, canvas.width / 2, canvas.height / 2);
  
  const labelTexture = new THREE.CanvasTexture(canvas);
  const labelMaterial = new THREE.MeshBasicMaterial({ 
    map: labelTexture,
    transparent: true
  });
  const labelGeometry = new THREE.PlaneGeometry(50, 12.5);
  const label = new THREE.Mesh(labelGeometry, labelMaterial);
  label.position.set(width/2, height - 20, 1);
  room.add(label);
  
  return room;
}

// Create a bed
function createBed() {
  const bed = new THREE.Group();
  
  // Bed frame
  const frameGeometry = new THREE.BoxGeometry(90, 20, 200);
  const frameMaterial = new THREE.MeshStandardMaterial({ 
    color: 0x8b4513, // Brown
    roughness: 0.8,
    metalness: 0.2
  });
  const frame = new THREE.Mesh(frameGeometry, frameMaterial);
  frame.position.set(45, 10, 100);
  frame.castShadow = true;
  frame.receiveShadow = true;
  bed.add(frame);
  
  // Mattress
  const mattressGeometry = new THREE.BoxGeometry(85, 15, 195);
  const mattressMaterial = new THREE.MeshStandardMaterial({ 
    color: 0xffffff, // White
    roughness: 0.7,
    metalness: 0.1
  });
  const mattress = new THREE.Mesh(mattressGeometry, mattressMaterial);
  mattress.position.set(45, 27.5, 100);
  mattress.castShadow = true;
  mattress.receiveShadow = true;
  bed.add(mattress);
  
  // Pillow
  const pillowGeometry = new THREE.BoxGeometry(70, 10, 40);
  const pillowMaterial = new THREE.MeshStandardMaterial({ 
    color: 0xf0f0f0, // Light white
    roughness: 0.5,
    metalness: 0.1
  });
  const pillow = new THREE.Mesh(pillowGeometry, pillowMaterial);
  pillow.position.set(45, 35, 30);
  pillow.castShadow = true;
  pillow.receiveShadow = true;
  bed.add(pillow);
  
  // Blanket
  const blanketGeometry = new THREE.BoxGeometry(85, 5, 140);
  const blanketMaterial = new THREE.MeshStandardMaterial({ 
    color: 0x4169e1, // Royal blue
    roughness: 0.9,
    metalness: 0.1
  });
  const blanket = new THREE.Mesh(blanketGeometry, blanketMaterial);
  blanket.position.set(45, 37.5, 130);
  blanket.castShadow = true;
  blanket.receiveShadow = true;
  bed.add(blanket);
  
  return bed;
}

// Create a desk
function createDesk() {
  const desk = new THREE.Group();
  
  // Desk top
  const topGeometry = new THREE.BoxGeometry(120, 5, 60);
  const topMaterial = new THREE.MeshStandardMaterial({ 
    color: 0xd2b48c, // Tan
    roughness: 0.7,
    metalness: 0.2
  });
  const top = new THREE.Mesh(topGeometry, topMaterial);
  top.position.set(60, 72.5, 30);
  top.castShadow = true;
  top.receiveShadow = true;
  desk.add(top);
  
  // Desk legs
  const legGeometry = new THREE.BoxGeometry(5, 70, 5);
  const legMaterial = new THREE.MeshStandardMaterial({ 
    color: 0xd2b48c, // Tan
    roughness: 0.8,
    metalness: 0.2
  });
  
  // Front-left leg
  const leg1 = new THREE.Mesh(legGeometry, legMaterial);
  leg1.position.set(10, 35, 5);
  leg1.castShadow = true;
  leg1.receiveShadow = true;
  desk.add(leg1);
  
  // Front-right leg
  const leg2 = new THREE.Mesh(legGeometry, legMaterial);
  leg2.position.set(110, 35, 5);
  leg2.castShadow = true;
  leg2.receiveShadow = true;
  desk.add(leg2);
  
  // Back-left leg
  const leg3 = new THREE.Mesh(legGeometry, legMaterial);
  leg3.position.set(10, 35, 55);
  leg3.castShadow = true;
  leg3.receiveShadow = true;
  desk.add(leg3);
  
  // Back-right leg
  const leg4 = new THREE.Mesh(legGeometry, legMaterial);
  leg4.position.set(110, 35, 55);
  leg4.castShadow = true;
  leg4.receiveShadow = true;
  desk.add(leg4);
  
  // Desk drawer
  const drawerGeometry = new THREE.BoxGeometry(40, 15, 50);
  const drawerMaterial = new THREE.MeshStandardMaterial({ 
    color: 0xc19a6b, // Darker tan
    roughness: 0.7,
    metalness: 0.2
  });
  const drawer = new THREE.Mesh(drawerGeometry, drawerMaterial);
  drawer.position.set(90, 62.5, 30);
  drawer.castShadow = true;
  drawer.receiveShadow = true;
  desk.add(drawer);
  
  // Drawer handle
  const handleGeometry = new THREE.BoxGeometry(20, 2, 2);
  const handleMaterial = new THREE.MeshStandardMaterial({ 
    color: 0x808080, // Gray
    roughness: 0.5,
    metalness: 0.8
  });
  const handle = new THREE.Mesh(handleGeometry, handleMaterial);
  handle.position.set(90, 62.5, 5);
  handle.castShadow = true;
  drawer.add(handle);
  
  return desk;
}

// Create a chair
function createChair() {
  const chair = new THREE.Group();
  
  // Seat
  const seatGeometry = new THREE.BoxGeometry(40, 5, 40);
  const seatMaterial = new THREE.MeshStandardMaterial({ 
    color: 0x8b4513, // Brown
    roughness: 0.8,
    metalness: 0.2
  });
  const seat = new THREE.Mesh(seatGeometry, seatMaterial);
  seat.position.set(20, 45, 20);
  seat.castShadow = true;
  seat.receiveShadow = true;
  chair.add(seat);
  
  // Backrest
  const backrestGeometry = new THREE.BoxGeometry(40, 40, 5);
  const backrestMaterial = new THREE.MeshStandardMaterial({ 
    color: 0x8b4513, // Brown
    roughness: 0.8,
    metalness: 0.2
  });
  const backrest = new THREE.Mesh(backrestGeometry, backrestMaterial);
  backrest.position.set(20, 67.5, 2.5);
  backrest.castShadow = true;
  backrest.receiveShadow = true;
  chair.add(backrest);
  
  // Legs
  const legGeometry = new THREE.CylinderGeometry(2, 2, 45, 8);
  const legMaterial = new THREE.MeshStandardMaterial({ 
    color: 0x696969, // Dark gray
    roughness: 0.5,
    metalness: 0.8
  });
  
  // Front-left leg
  const leg1 = new THREE.Mesh(legGeometry, legMaterial);
  leg1.position.set(5, 22.5, 5);
  leg1.castShadow = true;
  leg1.receiveShadow = true;
  chair.add(leg1);
  
  // Front-right leg
  const leg2 = new THREE.Mesh(legGeometry, legMaterial);
  leg2.position.set(35, 22.5, 5);
  leg2.castShadow = true;
  leg2.receiveShadow = true;
  chair.add(leg2);
  
  // Back-left leg
  const leg3 = new THREE.Mesh(legGeometry, legMaterial);
  leg3.position.set(5, 22.5, 35);
  leg3.castShadow = true;
  leg3.receiveShadow = true;
  chair.add(leg3);
  
  // Back-right leg
  const leg4 = new THREE.Mesh(legGeometry, legMaterial);
  leg4.position.set(35, 22.5, 35);
  leg4.castShadow = true;
  leg4.receiveShadow = true;
  chair.add(leg4);
  
  return chair;
}

// Create a dresser
function createDresser() {
  const dresser = new THREE.Group();
  
  // Body
  const bodyGeometry = new THREE.BoxGeometry(60, 80, 40);
  const bodyMaterial = new THREE.MeshStandardMaterial({ 
    color: 0xd2b48c, // Tan
    roughness: 0.7,
    metalness: 0.2
  });
  const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
  body.position.set(30, 40, 20);
  body.castShadow = true;
  body.receiveShadow = true;
  dresser.add(body);
  
  // Drawers
  const drawerGeometry = new THREE.BoxGeometry(56, 15, 1);
  const drawerMaterial = new THREE.MeshStandardMaterial({ 
    color: 0xc19a6b, // Darker tan
    roughness: 0.7,
    metalness: 0.2
  });
  
  // Create 4 drawers
  for (let i = 0; i < 4; i++) {
    const drawer = new THREE.Mesh(drawerGeometry, drawerMaterial);
    drawer.position.set(30, 15 + i*20, 0.5);
    body.add(drawer);
    
    // Drawer handle
    const handleGeometry = new THREE.CylinderGeometry(2, 2, 15, 8);
    const handleMaterial = new THREE.MeshStandardMaterial({ 
      color: 0x808080, // Gray
      roughness: 0.5,
      metalness: 0.8
    });
    const handle = new THREE.Mesh(handleGeometry, handleMaterial);
    handle.rotation.x = Math.PI / 2;
    handle.position.set(0, 0, -3);
    drawer.add(handle);
  }
  
  return dresser;
}

// Create a bookshelf
function createBookshelf() {
  const bookshelf = new THREE.Group();
  
  // Body
  const bodyGeometry = new THREE.BoxGeometry(80, 180, 30);
  const bodyMaterial = new THREE.MeshStandardMaterial({ 
    color: 0x8b4513, // Brown
    roughness: 0.8,
    metalness: 0.2
  });
  const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
  body.position.set(40, 90, 15);
  body.castShadow = true;
  body.receiveShadow = true;
  bookshelf.add(body);
  
  // Shelves
  const shelfGeometry = new THREE.BoxGeometry(76, 2, 28);
  const shelfMaterial = new THREE.MeshStandardMaterial({ 
    color: 0x8b4513, // Brown
    roughness: 0.8,
    metalness: 0.2
  });
  
  // Create 5 shelves
  for (let i = 0; i < 5; i++) {
    const shelf = new THREE.Mesh(shelfGeometry, shelfMaterial);
    shelf.position.set(40, 20 + i*40, 15);
    body.add(shelf);
  }
  
  // Add some books for visual interest
  const colors = [0xff0000, 0x00ff00, 0x0000ff, 0xffff00, 0xff00ff];
  
  for (let shelf = 0; shelf < 4; shelf++) {
    let offset = 0;
    
    // Add a random number of books to each shelf
    for (let i = 0; i < 5 + Math.floor(Math.random() * 3); i++) {
      const width = 5 + Math.random() * 10;
      const height = 20 + Math.random() * 10;
      
      const bookGeometry = new THREE.BoxGeometry(width, height, 20);
      const bookMaterial = new THREE.MeshStandardMaterial({ 
        color: colors[Math.floor(Math.random() * colors.length)],
        roughness: 0.8,
        metalness: 0.2
      });
      
      const book = new THREE.Mesh(bookGeometry, bookMaterial);
      book.position.set(offset - 30, 40 + shelf*40, 15);
      offset += width + 2;
      body.add(book);
    }
  }
  
  return bookshelf;
}

// Create a minifridge
function createMinifridge() {
  const minifridge = new THREE.Group();
  
  // Body
  const bodyGeometry = new THREE.BoxGeometry(50, 85, 50);
  const bodyMaterial = new THREE.MeshStandardMaterial({ 
    color: 0xffffff, // White
    roughness: 0.9,
    metalness: 0.1
  });
  const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
  body.position.set(25, 42.5, 25);
  body.castShadow = true;
  body.receiveShadow = true;
  minifridge.add(body);
  
  // Door edge (create a subtle border)
  const doorEdgeGeometry = new THREE.BoxGeometry(48, 83, 1);
  const doorEdgeMaterial = new THREE.MeshStandardMaterial({ 
    color: 0xe0e0e0, // Light gray
    roughness: 0.9,
    metalness: 0.1
  });
  const doorEdge = new THREE.Mesh(doorEdgeGeometry, doorEdgeMaterial);
  doorEdge.position.set(25, 42.5, 0.5);
  body.add(doorEdge);
  
  // Handle
  const handleGeometry = new THREE.BoxGeometry(3, 20, 2);
  const handleMaterial = new THREE.MeshStandardMaterial({ 
    color: 0x808080, // Gray
    roughness: 0.5,
    metalness: 0.8
  });
  const handle = new THREE.Mesh(handleGeometry, handleMaterial);
  handle.position.set(-20, 50, -1);
  doorEdge.add(handle);
  
  // Fridge logo (simple colored square)
  const logoGeometry = new THREE.PlaneGeometry(10, 10);
  const logoMaterial = new THREE.MeshBasicMaterial({ 
    color: 0x0000ff, // Blue
  });
  const logo = new THREE.Mesh(logoGeometry, logoMaterial);
  logo.position.set(0, 70, 0.6);
  doorEdge.add(logo);
  
  return minifridge;
}

// Create a microwave
function createMicrowave() {
  const microwave = new THREE.Group();
  
  // Body
  const bodyGeometry = new THREE.BoxGeometry(40, 25, 30);
  const bodyMaterial = new THREE.MeshStandardMaterial({ 
    color: 0x303030, // Dark gray
    roughness: 0.9,
    metalness: 0.3
  });
  const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
  body.position.set(20, 12.5, 15);
  body.castShadow = true;
  body.receiveShadow = true;
  microwave.add(body);
  
  // Door
  const doorGeometry = new THREE.PlaneGeometry(25, 20);
  const doorMaterial = new THREE.MeshStandardMaterial({ 
    color: 0x000000, // Black
    transparent: true,
    opacity: 0.7,
    roughness: 0.1,
    metalness: 0.9
  });
  const door = new THREE.Mesh(doorGeometry, doorMaterial);
  door.position.set(0, 12.5, 15.1);
  body.add(door);
  
  // Control panel
  const panelGeometry = new THREE.PlaneGeometry(10, 20);
  const panelMaterial = new THREE.MeshStandardMaterial({ 
    color: 0x202020, // Very dark gray
    roughness: 0.9,
    metalness: 0.3
  });
  const panel = new THREE.Mesh(panelGeometry, panelMaterial);
  panel.position.set(17.5, 12.5, 15.1);
  body.add(panel);
  
  // Buttons (simple colored squares)
  for (let i = 0; i < 9; i++) {
    const row = Math.floor(i / 3);
    const col = i % 3;
    
    const buttonGeometry = new THREE.PlaneGeometry(2, 2);
    const buttonMaterial = new THREE.MeshBasicMaterial({ 
      color: 0xffffff, // White
    });
    const button = new THREE.Mesh(buttonGeometry, buttonMaterial);
    button.position.set(15 + col*3, 17 - row*3, 15.2);
    body.add(button);
  }
  
  return microwave;
}

// Create a lamp
function createLamp() {
  const lamp = new THREE.Group();
  
  // Base
  const baseGeometry = new THREE.CylinderGeometry(10, 12, 5, 16);
  const baseMaterial = new THREE.MeshStandardMaterial({ 
    color: 0xc0c0c0, // Silver
    roughness: 0.3,
    metalness: 0.8
  });
  const base = new THREE.Mesh(baseGeometry, baseMaterial);
  base.position.set(0, 2.5, 0);
  base.castShadow = true;
  base.receiveShadow = true;
  lamp.add(base);
  
  // Stem
  const stemGeometry = new THREE.CylinderGeometry(2, 2, 35, 8);
  const stemMaterial = new THREE.MeshStandardMaterial({ 
    color: 0xc0c0c0, // Silver
    roughness: 0.3,
    metalness: 0.8
  });
  const stem = new THREE.Mesh(stemGeometry, stemMaterial);
  stem.position.set(0, 22.5, 0);
  stem.castShadow = true;
  stem.receiveShadow = true;
  lamp.add(stem);
  
  // Shade
  const shadeGeometry = new THREE.ConeGeometry(15, 20, 16, 1, true);
  const shadeMaterial = new THREE.MeshStandardMaterial({ 
    color: 0xfffaf0, // Cream
    roughness: 0.9,
    metalness: 0.1,
    side: THREE.DoubleSide
  });
  const shade = new THREE.Mesh(shadeGeometry, shadeMaterial);
  shade.position.set(0, 40, 0);
  shade.rotation.x = Math.PI;
  shade.castShadow = true;
  lamp.add(shade);
  
  // Light (point light)
  const light = new THREE.PointLight(0xffffcc, 0.5, 100);
  light.position.set(0, 35, 0);
  light.castShadow = true;
  light.shadow.mapSize.width = 512;
  light.shadow.mapSize.height = 512;
  lamp.add(light);
  
  return lamp;
}

// Create a storage bin
function createStorageBin() {
  const storageBin = new THREE.Group();
  
  // Box
  const boxGeometry = new THREE.BoxGeometry(60, 30, 40);
  const boxMaterial = new THREE.MeshStandardMaterial({ 
    color: 0x6495ed, // Cornflower blue
    roughness: 0.9,
    metalness: 0.1
  });
  const box = new THREE.Mesh(boxGeometry, boxMaterial);
  box.position.set(30, 15, 20);
  box.castShadow = true;
  box.receiveShadow = true;
  storageBin.add(box);
  
  // Lid
  const lidGeometry = new THREE.BoxGeometry(60, 5, 40);
  const lidMaterial = new THREE.MeshStandardMaterial({ 
    color: 0x4682b4, // Steel blue (slightly darker)
    roughness: 0.9,
    metalness: 0.1
  });
  const lid = new THREE.Mesh(lidGeometry, lidMaterial);
  lid.position.set(30, 32.5, 20);
  lid.castShadow = true;
  lid.receiveShadow = true;
  storageBin.add(lid);
  
  // Handle
  const handleGeometry = new THREE.BoxGeometry(20, 3, 5);
  const handleMaterial = new THREE.MeshStandardMaterial({ 
    color: 0x4682b4, // Steel blue
    roughness: 0.5,
    metalness: 0.5
  });
  const handle = new THREE.Mesh(handleGeometry, handleMaterial);
  handle.position.set(30, 35, 20);
  handle.castShadow = true;
  lid.add(handle);
  
  return storageBin;
}

// Create a bulletin board
function createBulletinBoard() {
  const board = new THREE.Group();
  
  // Frame
  const frameGeometry = new THREE.BoxGeometry(80, 60, 2);
  const frameMaterial = new THREE.MeshStandardMaterial({ 
    color: 0x8b4513, // Brown
    roughness: 0.8,
    metalness: 0.2
  });
  const frame = new THREE.Mesh(frameGeometry, frameMaterial);
  frame.position.set(40, 30, 1);
  frame.castShadow = true;
  frame.receiveShadow = true;
  board.add(frame);
  
  // Cork background
  const corkGeometry = new THREE.PlaneGeometry(76, 56);
  const corkMaterial = new THREE.MeshStandardMaterial({ 
    color: 0xdeb887, // Burlywood
    roughness: 1.0,
    metalness: 0.0
  });
  const cork = new THREE.Mesh(corkGeometry, corkMaterial);
  cork.position.set(40, 30, 1.1);
  board.add(cork);
  
  // Add some notes (simple colored squares)
  const colors = [0xffffff, 0xffff99, 0x99ff99, 0x9999ff, 0xff9999];
  
  for (let i = 0; i < 6; i++) {
    const noteSize = 10 + Math.random() * 5;
    
    const noteGeometry = new THREE.PlaneGeometry(noteSize, noteSize);
    const noteMaterial = new THREE.MeshBasicMaterial({ 
      color: colors[Math.floor(Math.random() * colors.length)],
    });
    const note = new THREE.Mesh(noteGeometry, noteMaterial);
    
    // Random position within the cork board
    const x = 40 + (Math.random() * 60 - 30);
    const y = 30 + (Math.random() * 40 - 20);
    
    note.position.set(x, y, 1.2);
    
    // Random rotation
    note.rotation.z = (Math.random() * 0.4) - 0.2;
    
    board.add(note);
  }
  
  // Add some pins
  for (let i = 0; i < 8; i++) {
    const pinGeometry = new THREE.SphereGeometry(1, 8, 8);
    const pinMaterial = new THREE.MeshStandardMaterial({ 
      color: Math.random() > 0.5 ? 0xff0000 : 0x0000ff, // Red or blue
      roughness: 0.5,
      metalness: 0.8
    });
    const pin = new THREE.Mesh(pinGeometry, pinMaterial);
    
    // Random position within the cork board
    const x = 40 + (Math.random() * 70 - 35);
    const y = 30 + (Math.random() * 50 - 25);
    
    pin.position.set(x, y, 1.5);
    board.add(pin);
  }
  
  return board;
}

function createObject(container) {
  const group = new THREE.Group();
  // Create room
  const room = createRoom("Jones Hall 101", 300, 250, 240, "single");
  group.add(room);

  // Add furniture items
  const bed = createBed();
  bed.position.set(30, 0, 30);
  bed.rotation.y = 0;
  group.add(bed);

  // More furniture...

  // Add lamp on top of desk
  const lamp = createLamp();
  lamp.position.set(80, 75, 170);
  lamp.rotation.y = 0;
  group.add(lamp);

  return group;
}