function createObject(container) {
  // Create a group to hold all objects
  const group = new THREE.Group();

  // ==== Trunk ====
  // Cylinder for trunk
  const trunkHeight = 1.2;
  const trunkRadiusTop = 0.11;
  const trunkRadiusBottom = 0.15;
  const trunkGeometry = new THREE.CylinderGeometry(trunkRadiusTop, trunkRadiusBottom, trunkHeight, 16);
  const trunkMaterial = new THREE.MeshPhongMaterial({ color: 0x8d5524, flatShading: true });
  const trunkMesh = new THREE.Mesh(trunkGeometry, trunkMaterial);
  trunkMesh.position.y = trunkHeight / 2;
  group.add(trunkMesh);

  // ==== Foliage ====
  // Three overlapping spheres (or cones) for a stylized "leafy" crown
  const foliageMaterial = new THREE.MeshPhongMaterial({ color: 0x2e8b57, flatShading: true });

  // Bottom foliage
  const foliageGeom1 = new THREE.SphereGeometry(0.5, 16, 12);
  const foliageMesh1 = new THREE.Mesh(foliageGeom1, foliageMaterial);
  foliageMesh1.position.y = trunkHeight + 0.28;
  group.add(foliageMesh1);

  // Middle foliage (slightly smaller, shifted up)
  const foliageGeom2 = new THREE.SphereGeometry(0.4, 16, 12);
  const foliageMesh2 = new THREE.Mesh(foliageGeom2, foliageMaterial);
  foliageMesh2.position.y = trunkHeight + 0.60;
  group.add(foliageMesh2);

  // Top foliage (smaller, higher)
  const foliageGeom3 = new THREE.SphereGeometry(0.27, 16, 12);
  const foliageMesh3 = new THREE.Mesh(foliageGeom3, foliageMaterial);
  foliageMesh3.position.y = trunkHeight + 0.87;
  group.add(foliageMesh3);

  // ==== Roots (optional, stylize base) ====
  // Add 3-4 small cones as buttress roots
  const rootColor = 0x6b3e16;
  const rootMaterial = new THREE.MeshPhongMaterial({ color: rootColor, flatShading: true });
  const rootGeometry = new THREE.ConeGeometry(0.08, 0.15, 8);
  const rootCount = 3;
  for (let i = 0; i < rootCount; i++) {
    const angle = (i / rootCount) * Math.PI * 2;
    const rootMesh = new THREE.Mesh(rootGeometry, rootMaterial);
    rootMesh.rotation.x = Math.PI;
    rootMesh.position.set(
      Math.cos(angle) * 0.11,
      0.075,
      Math.sin(angle) * 0.11
    );
    group.add(rootMesh);
  }

  // Center the group at the base of the trunk
  group.position.y = 0;

  return group;
}