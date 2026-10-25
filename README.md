### AI-Powered Subterranean Exploration and Rescue System

**Application ID:** VK26-IITH-SM-0043 | **Vishwakarma Awards 2026-27**

---

## At a Glance

| | |
| --- | --- |
| **Platform** | Tracked chassis with differential steering |
| **High-level brain** | Raspberry Pi |
| **Low-level control** | ESP32 |
| **CAD** | FreeCAD |
| **Schematic** | EasyEDA |
| **Status** | In development |

## Start Here

| If you want to... | Go to |
| --- | --- |
| See the rover in 3D | [Live 3D model](https://rover-chasis.vercel.app/) |
| Open or rebuild the CAD model | [CAD.md](CAD.md) |
| Open the schematic diagram | [schematic.md](schematic.md) |
| Browse the project files | [Google Drive](https://drive.google.com/drive/folders/1EkdNMd7naFCUVERvC5URtl4ZttO6ABKr?usp=sharing) |

---

## Overview

The Tank Rover is a tracked mobile robotic platform being developed as part of the **Vishwakarma Awards initiative**. The project aims to develop a compact, modular, and cost-effective robotic system capable of controlled movement, obstacle detection, environmental sensing, and future expansion toward indoor mapping and autonomous navigation.

The platform uses a **Raspberry Pi for high-level processing** and an **ESP32 for low-level hardware control and peripheral interfacing**. This separation enables computationally intensive tasks to be handled independently from time-sensitive control operations.

The rover is built around a tracked chassis, providing a practical platform for movement across varied indoor surfaces and uneven terrain within the limits of its mechanical design.

## Project Objectives

- Develop a functional tracked mobile rover with reliable movement and steering.
- Implement differential steering by independently controlling the left and right track drive systems.
- Integrate motor drivers, power management, and embedded control electronics.
- Interface with sensors for distance measurement and obstacle detection.
- Establish communication between the Raspberry Pi and ESP32 for high-level commands and low-level control.
- Create a modular hardware and software architecture that supports future upgrades.
- Provide a foundation for indoor mapping, localization, and autonomous navigation.

## System Architecture

The rover follows a two-level control architecture: a thinking layer and a doing layer.

```text
   Cameras and LiDAR
          |
          v
 +------------------+   UART   +----------------+     +--------------+
 |   Raspberry Pi   |<-------->|     ESP32      |---->| Motor driver |
 | high-level logic |          | low-level ctrl |     +------+-------+
 +------------------+          +-------+--------+            |
                                       ^               +-----+------+
                                       |               |            |
                          Distance and environment  Left motor   Right motor
                                  sensors           + encoder    + encoder
```

*Planned architecture. The encoders feed their readings back to the ESP32.*

<details>
<summary><b>1. Raspberry Pi: high-level processing</b></summary>

<br>

The Raspberry Pi serves as the rover's primary computing platform. Its responsibilities may include:

- Processing high-level movement commands.
- Coordinating sensor data and system-level logic.
- Implementing obstacle avoidance and navigation algorithms.
- Supporting future mapping and localization capabilities.
- Handling communication with a remote control interface, where implemented.

</details>

<details>
<summary><b>2. ESP32: embedded control</b></summary>

<br>

The ESP32 handles hardware-level control and interfaces with the rover's peripherals. Its responsibilities may include:

- Receiving movement commands from the Raspberry Pi.
- Generating control signals for the motor driver.
- Controlling the left and right track drive systems.
- Reading supported sensors and reporting measurements.
- Managing low-level communication and basic safety responses.

</details>

<details>
<summary><b>3. Communication between controllers</b></summary>

<br>

A suitable interface, such as UART, will connect the Raspberry Pi and ESP32. The final communication protocol and command format will be documented as the system design is finalized.

</details>

## Planned Development

Development will proceed one step at a time:

```text
Basic mobility > Remote control > Sensor integration > Obstacle avoidance > Mapping > Validation
```

| Stage | Goal |
| --- | --- |
| **1. Basic mobility** | Establish reliable forward, reverse, turning, and stopping operations. |
| **2. Remote control** | Enable command-based rover operation and verify communication between the controllers. |
| **3. Sensor integration** | Add and validate distance measurement and obstacle detection. |
| **4. Obstacle avoidance** | Implement and test reactive obstacle-avoidance behaviour. |
| **5. Mapping and localization** | Explore indoor spatial mapping and position estimation, subject to the available sensors and processing capabilities. |
| **6. System validation** | Evaluate movement, control reliability, sensor performance, and overall system behaviour. |

> **Note:** These stages describe the intended development path. Capabilities will be marked as implemented only after testing.

## Repository Structure

```text
.
├── README.md        Project overview (this file)
├── schematic.md     How to open the schematic diagram
├── CAD.md           How to view the CAD model and run an FEA
└── assets/
    ├── schematic/   EasyEDA project and schematic PDF
    ├── cad/         CAD files
    └── bom/         Bill of materials
```

## Design Approach

The project follows a modular engineering approach:

**Design, implement, test, document, improve. Repeat.**

Hardware interfaces and software components will be documented to simplify debugging, integration, maintenance, and future expansion. The repository serves as the central technical record of the rover's design, implementation, and development progress.

## Developers

| Name | GitHub |
| --- | --- |
| Vishnu Kaushik S | [VISHNU-KAUSHIK-S](https://github.com/VISHNU-KAUSHIK-S) |
| Kevin Raymond | [kevinraymond93](https://github.com/kevinraymond93) |
| Arnav Rath | [arnav-rath11](https://github.com/arnav-rath11/arnav-rath11) |
| Vikas D K | [Vikas-Dk-2005](https://github.com/Vikas-Dk-2005) |

---

*Built for the Vishwakarma Awards 2026-27.*
