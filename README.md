# Explaining the Math: Mapping Soil Depths on Minirhizotron Tube Images for Root Analysis

## The Big Picture: Why Soil Layers Look Wavy Inside a Minirhizotron Tube

For studying plant roots without disturbing them, researchers often install transparent tubes called **Minirhizotron tubes** into the soil at an angle. A special camera, like a **CID-602**, is inserted into the tube to take pictures of the roots growing against the tube's wall, visible through the transparent surface. The camera captures a 360° view at various points inside the tube. The software then "unrolls" this cylindrical picture into a flat, rectangular image, similar to how you'd flatten out a paper towel roll after cutting it open.

The challenge is that because the Minirhizotron tube is put into the ground at a slant (not straight down), the perfectly flat, horizontal soil layers in the ground won't appear as straight horizontal lines on the unrolled image. Instead, they will look like **wavy (sinusoidal) curves**.

This document explains the underlying geometry that creates these waves and provides the mathematical steps used by software to accurately draw lines on the unrolled image corresponding to specific horizontal soil depths.

### What We Have:

*   **Ground:** A flat surface (like the ground level, considered z=0), with soil layers stacked perfectly horizontally below it.
*   **Minirhizotron Tube:** A straight, transparent, right-circular tube with a constant radius R, inserted into the soil at a specific tilt angle (θ, measured above the horizontal ground).
*   **CID-602 Camera:** A camera designed to capture images of the inner wall of the tube (and the soil/roots visible through it).
*   **Unrolled Image:** A flat picture created by "unwrapping" the 360° cylindrical view captured by the camera.

### The Goal:

For plant biologists studying roots, it's crucial to know the exact depth of the roots they see in the image. The goal of this algorithm is to use geometry and math to draw accurate wavy lines on the unrolled image that show exactly where each original horizontal soil depth (like 10cm deep, 20cm deep) intersects the tube wall. This allows for precise root analysis by depth.

## Step 1: Where Are We Measuring From? Our Points of View

To locate anything precisely, we need a system for describing positions. We'll use three ways to describe where a point is:

1.  **Real-World Spot (x, y, z):** This is like giving directions in the actual physical space.
    *   We set our starting point (0,0,0) where the Minirhizotron tube enters the ground surface.
    *   x: Horizontal distance, in the direction the tube was inserted.
    *   y: Horizontal distance, sideways (perpendicular to the insertion direction).
    *   z: Vertical distance (positive means up, negative means down into the soil – so a depth `d` is at `z = -d`).
2.  **Tube Surface Spot (s, φ):** This describes a point based on its position *on the surface of the tube*.
    *   s: The distance measured along the *center line* of the tube, starting from where the tube enters the ground.
    *   φ (phi): The angular position measured *around* the tube (like 0° to 360°, or 0 to 2π radians). Imagine a line along the "top" of the tube relative to its tilt angle; φ is the angle from that line as you wrap around the circle.
    *   The distance from the tube's center to the point is always the radius R because we are on the tube's wall.
3.  **Image Spot (u, v):** This describes where the point appears on the flat, unrolled picture from the camera.
    *   u: Horizontal position on the unrolled image (from the left edge, say u=0, to the right edge, u=W, the image width).
    *   v: Vertical position on the unrolled image (from the top edge, say v=0, to the bottom edge, v=H, the image height).

## Step 2: Tracing the Minirhizotron Tube's Center Line

Let's follow the path of the very center line of the Minirhizotron tube as it goes into the ground at angle θ.

Imagine a tiny dot moving along the very center of the tube. If it travels a distance 's' along the center line from where it entered the ground (our (0,0,0) start), where is it in the real world (x, y, z)?

*   The tube is tilted at angle θ above the horizontal ground (the x-y plane).
*   As the dot moves 's' distance along this tilted line:
    *   Its horizontal movement in the insertion direction (x) is like the length of its shadow on the ground: `s * cos(θ)`.
    *   Its vertical movement downwards (z) is related to the height it drops. Since it's going down into the soil, the z-coordinate becomes more negative: `-s * sin(θ)`.
    *   It doesn't move sideways (y = 0) from the initial line of insertion in the x-z plane.

So, the real-world (x, y, z) position of the center of the Minirhizotron tube at distance 's' along its axis is:
**(s cos(θ), 0, -s sin(θ))**

## Step 3: Finding the Real-World Position of *Any* Point on the Tube Wall

Now, consider a point not just at the center, but *on the transparent wall* of the tube. To find its real-world (x, y, z) spot, we can start at the center point (from Step 2) and move directly outwards by the tube's radius R, in the direction given by the angle φ around the tube.

Think about the circular cross-section of the tube at distance 's' along its axis. This circle is tilted because the tube is tilted. The math figures out how to describe this "outward" movement (a vector of length R, pointing at angle φ *within the tilted circular plane*) using our standard x, y, and z directions.

The math shows that adding this outward movement to the center point's coordinates gives the following real-world (x, y, z) position for a point P on the tube surface at distance 's' and angle 'φ':

**P(s,φ) = [s cos(θ) + R cos(φ) sin(θ), R sin(φ), -s sin(θ) + R cos(φ) cos(θ)]**

*   The first part (s cos(θ), 0, -s sin(θ)) is the real-world location of the tube's center at distance 's'.
*   The second parts (R cos(φ) sin(θ), R sin(φ), R cos(φ) cos(θ)) are the components of the vector pointing from the center outwards to the surface point at angle φ, translated into the real-world x, y, and z directions.

**Critical Insight**: Look closely at the z-coordinate (depth) part: `-s sin(θ) + R cos(φ) cos(θ)`. The depth of a point on the tube wall depends on both how far along the tube you are ('s') *and* your angular position around the tube ('φ'). This interdependence is the key geometric reason why horizontal depth layers appear as wavy lines on the unrolled image!

## Step 4: Finding Where a Horizontal Soil Layer Intersects the Tube Wall

A horizontal soil layer at a specific depth 'd' is simply the collection of all points in the real world where the z-coordinate is equal to -d. We want to find the points on the Minirhizotron tube wall that have this specific z-coordinate.

We take the z-coordinate part of our wall point formula from Step 3 and set it equal to -d:
`-s sin(θ) + R cos(φ) cos(θ) = -d`

Now, we solve this equation to find 's' (the distance along the tube axis) in terms of the depth 'd' and the angle 'φ' around the tube wall. This tells us, for a given depth and angle, how far down the tube the soil layer appears.

Rearranging the equation to isolate 's':

`s sin(θ) = d - R cos(φ) cos(θ)`

`s = (d - R cos(φ) cos(θ)) / sin(θ)`

**Big Aha Moment:** Look at this formula for 's'. For a fixed depth 'd', the value of 's' is *not* constant. It changes depending on `cos(φ)`. This is the fundamental discovery that explains the wavy pattern!

### What This Means Physically:

*   Imagine the tilted tube. The part of the tube wall that's highest up towards the ground surface (where φ = 0 relative to the tilt, corresponding to `cos(φ) = 1`) reaches depth 'd' sooner, meaning a smaller value of 's'.
*   The part of the tube wall that's lowest down (where φ = π or 180°, corresponding to `cos(φ) = -1`) reaches the same depth 'd' later, meaning a larger value of 's'.
*   As you move around the tube wall (change φ from 0 to 2π), the distance 's' at which a horizontal depth layer intersects the wall varies following a cosine curve.

## Step 5: Translating Tube Positions to Image Positions

The CID-602 camera software takes the cylindrical view and "unrolls" it into a flat, rectangular image. This transformation maps positions on the tube surface (described by s and φ) to pixel locations on the image (described by u and v).

*   **Angle around the tube (φ) maps to Horizontal position on the image (u):** Going all the way around the tube (0 to 2π radians or 0 to 360 degrees) corresponds to going all the way across the unrolled image (from u=0 to u=W, the image width). The horizontal pixel position 'u' is a simple scaling of the angle φ:
    `u = (φ / 2π) × W`
    (This means φ = (u / W) × 2π if we need to go the other way)

*   **Distance along the tube (s) maps to Vertical position on the image (v):** The distance 's' measured along the tube's axis corresponds directly to the vertical position 'v' on the unrolled image. Imagine cutting the tube and flattening it – lines parallel to the tube's axis become vertical lines on the image. The distance along these lines is 's'.
    The exact mapping depends on how the image is scaled vertically. The formula typically used is:
    `v = H - (s × pixels_per_cm_y)`
    Here, H is likely the total image height or a reference vertical position (e.g., the bottom of the image), and `pixels_per_cm_y` is the conversion factor from real-world distance 's' (in cm) to image pixels. The `H - ...` part means that larger values of 's' (further down the tube into the ground) correspond to smaller values of 'v' (higher up on the image, assuming v=0 is the top).

## Step 6: Putting It All Together - The Final Formula for Drawing Depth Lines

We want a formula that tells us, for any horizontal pixel column 'u' on the unrolled image, what vertical pixel row 'v' corresponds to a specific horizontal soil depth 'd'.

We have established the connections:
1.  `v` depends on `s` (from Step 5).
2.  `s` depends on `d` and `φ` (from Step 4).
3.  `φ` depends on `u` (from Step 5).

By substituting the expressions for `s` and `φ` into the equation for `v`, we get the complete formula for the vertical pixel position `v` as a function of the horizontal pixel position `u` and the desired depth `d`:

`v(u,d) = H - [ (d - R cos( (u / W) × 2π ) cos(θ)) / sin(θ) ] × pixels_per_cm_y`

This is the core formula the software uses! For every horizontal position `u` across the image, it calculates the corresponding `v` to draw the point for depth `d`. Connecting these points creates the wavy depth line.

The formula is usually written to separate the constant part related to the overall depth level from the part that creates the wave:

`v(u,d) = [H - (d / sin(θ)) × pixels_per_cm_y] + [(R cos(θ) / sin(θ)) × cos(2πu/W) × pixels_per_cm_y]`

### Understanding the Final Formula's Meaning:

*   **Part 1: The Average Line Position** `[H - (d / sin(θ)) × pixels_per_cm_y]`
    *   This part is a constant value for a given depth `d` and tube angle `θ`. It determines the overall average vertical level of the depth line on the image.
    *   Deeper soil layers (larger `d`) will result in a smaller `v` value (meaning they are drawn higher up on the image, assuming v=0 is the top).
*   **Part 2: The Sinusoidal (Wavy) Pattern** `[(R cos(θ) / sin(θ)) × cos(2πu/W) × pixels_per_cm_y]`
    *   This part creates the characteristic wave shape. It changes as you move across the image (as 'u' changes) because of the `cos(2πu/W)` term.
    *   The term `cos(2πu/W)` goes through exactly one full wave cycle (from its maximum to minimum and back) as 'u' goes from the left edge (0) to the right edge (W) of the image. This corresponds to going once around the tube (0 to 2π in φ).
    *   The number `(R cos(θ) / sin(θ)) × pixels_per_cm_y` is the wave's **amplitude** – it controls how tall or deep the wave is.
        *   It depends on the tube's radius R: A wider Minirhizotron tube leads to taller waves.
        *   It depends significantly on the tilt angle θ:
            *   If θ is close to 90° (tube nearly vertical), cos(θ) is small, and the amplitude is small. The wave flattens out, and the depth line becomes nearly horizontal – which makes perfect sense for a vertical tube!
            *   If θ is small (tube nearly horizontal), sin(θ) is small, `cos(θ)/sin(θ)` is large, leading to very large amplitude waves.

## Step 7: Practical Implementation - Using the Math for Root Analysis

The algorithm doesn't just draw lines; it allows researchers to use these lines to identify and analyze roots at specific depths.

By calculating the curve points for each desired depth line using the formula, the software can:
*   Visually show the user exactly where different depth levels (e.g., 0-10cm, 10-20cm) cross the image.
*   Mathematically define the image region *between* two consecutive depth lines as a specific soil layer. This allows for automated or manual analysis (like counting or measuring roots) strictly within that depth range.

This often involves generating a mask or polygon on the image that outlines the area between the calculated upper and lower depth curves for a given layer.

## Handling the Angle Convention

A practical detail for implementation is how the tilt angle θ is defined. Users typically specify an angle like "30 degrees above horizontal". The mathematical formulas need to be consistent with this definition. Sometimes, the math might internally use an angle relative to the vertical or a different convention. The code needs to ensure the input angle is correctly converted (e.g., if the math expects the angle from vertical, a 30° angle above horizontal is `90° - 30° = 60°` from vertical). The sine and cosine values derived from the user's angle θ must match the `sin(θ)` and `cos(θ)` used in the formula based on the coordinate system definition.

## Validation and What the Formulas Need

The math behind this algorithm is based on the exact geometry of a tilted cylinder intersecting a flat plane. The formulas are accurate provided:
1.  The Minirhizotron tube is inserted at an angle (`0° < θ < 90°`). The formula produces straight lines (horizontal or vertical, depending on the specific geometry setup) in the edge cases of perfectly vertical or horizontal tubes, but the formula itself involves division by `sin(θ)`, which is zero at 0° and 180°, requiring special handling for purely horizontal insertion.
2.  We are interested in actual depths below the surface (`d > 0`).
3.  We are considering points along the tube that are physically in the ground (`s ≥ 0`).

## Summary and Key Takeaways

1.  **The Problem**: Horizontal soil layers look wavy on flat images from tilted Minirhizotron tubes because of the 3D geometry.
2.  **The Cause**: A horizontal plane (soil layer) intersects a tilted cylinder (Minirhizotron tube) such that the points of intersection are at different distances along the cylinder axis (`s`) depending on the angle around the cylinder (`φ`). This variation in 's' is sinusoidal with respect to 'φ'.
3.  **The Solution**: Use trigonometry and coordinate transformations to derive a formula (`v(u,d)`) that maps a horizontal pixel position (`u`) and a desired real-world depth (`d`) to the correct vertical pixel position (`v`) on the unrolled image.
4.  **The Result**: Accurate depth lines that are not arbitrary curves, but precise sinusoidal waves whose shape and position are determined by the tube's radius, the insertion angle, and the depth.

By understanding and implementing this geometry, Minirhizotron camera systems like the CID-602 and their analysis software can accurately provide depth-specific information on the unrolled images, allowing plant biologists to precisely study root development within different soil layers. The wavy pattern isn't a distortion; it's the correct geometric representation of horizontal depths seen from the perspective of a tilted tube wall.
