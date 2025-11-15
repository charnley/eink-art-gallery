
# Building Your Own AI & E-Ink Powered Art Gallery

![https://charnley.github.io/blog/assets/images/eink_art/photos/front_double_landscapes.jpg](https://charnley.github.io/blog/assets/images/eink_art/photos/front_double_landscapes.jpg)


The write-up can be found at [https://charnley.github.io/blog/2025/04/02/e-ink-ai-esp32-local-art-gallery.html](https://charnley.github.io/blog/2025/04/02/e-ink-ai-esp32-local-art-gallery.html)

The different services can be found `/services/*`.

```mermaid
graph TD

    subgraph Desktop [Desktop Computer]
      direction RL
      gpucron@{ shape: rounded, label: "Cron job" }
      GPU@{ shape: rounded, label: "GPU" }
      gpucron --> GPU
    end

    subgraph HA [Home Assistant]
      database@{ shape: db, label: ".sqlite" }
      canvasserver@{ shape: rounded, label: "Picture\nServer" }
      canvasserver --> database
    end

    subgraph pictures [Picture Frames]

        subgraph esp32 [ESP32]
            esp32eink@{ shape: rounded, label: "E-Ink\nDisplay" }
        end
        subgraph rpi [Raspberry Pi Zero]
            rpieink@{ shape: rounded, label: "E-Ink\nDisplay" }
        end

        canvasserver -- "POST image" --> rpi
        esp32 -- GET image --> canvasserver

    end

    gpucron -- "GET status" --> canvasserver
    gpucron -- POST image(s) --> canvasserver

    classDef default stroke-width:2px;
    classDef default fill: transparent;
    classDef ParentGraph fill: transparent, stroke-width:2px;
    class pictures,HA,Desktop,esp32,rpi ParentGraph
```


## Database Workflow

```mermaid
erDiagram
    FrameGroup ||--o{ Frame : "contains"
    FrameGroup ||--o{ FrameGroupPrompt : "activates"
    Prompt ||--o{ FrameGroupPrompt : "activated_by"
    Prompt ||--o{ Image : "generates"
    Frame ||--o{ FrameBatteryState : "monitors"

    FrameGroup {
        uuid id PK
        string name
        string schedule_frame
        string schedule_prompt
        boolean default
    }

    Frame {
        uuid id PK
        FrameType type
        WaveshareDisplay model
        string mac
        string endpoint
        uuid group_id FK
    }

    Prompt {
        string id PK
        string prompt
        string image_model
        WaveshareDisplay display_model
    }

    Image {
        uuid id PK
        string prompt FK
        bytes image_data
    }

    FrameGroupPrompt {
        uuid group_id PK,FK
        string prompt_id PK,FK
    }

    FrameBatteryState {
        uuid frame_id PK,FK
        datetime timestamp PK
        float voltage
    }
```

```mermaid
flowchart TD
    subgraph "Art Generation Workflow"
        A[Create Prompt] --> B[Generate Images]
        B --> C[Store Images]
        C --> D[Associate with Prompt]
    end

    subgraph "Frame Management"
        E[Create FrameGroup] --> F[Set Schedules]
        F --> G[Add Frames to Group]
        G --> H[Activate Prompts]
    end

    subgraph "PULL Frame Workflow (ESP32)"
        I1[ESP32 wakes up] --> J1[Request Image via MAC]
        J1 --> K1[Get Frame's Group]
        K1 --> L1[Select Active Prompt]
        L1 --> M1[Get Random Image]
        M1 --> N1[Return Image to ESP32]
        N1 --> O1[ESP32 displays image]
        O1 --> P1[Record Battery State]
        P1 --> Q1[ESP32 goes to sleep]
    end

    subgraph "PUSH Frame Workflow (Raspberry Pi)"
        I2[Cron triggers] --> J2[Get Group's PUSH Frames]
        J2 --> K2[Select Active Prompt]
        K2 --> L2[Get Random Image]
        L2 --> M2[POST Image to Frame API]
        M2 --> N2[Raspberry Pi displays image]
    end

    subgraph "Scheduled Operations"
        R1[Cron: Prompt Rotation] --> S1[Rotate Group Prompts]
        R2[Cron: Frame Update] --> S2[Trigger PUSH Frame Workflow]
    end

    D --> H
    H --> L1
    H --> K2
    S1 --> H
    S2 --> I2
```

- The **picture server** stores a list of AI prompts, each with its associated images, in an SQLite database. For our setup, this is hosted on **Home Assistant as an Add-on**, but it could easily run on any Docker hosting service.
- Every night, the **desktop computer** checks the picture server for prompts that need images. For each prompt, the desktop computer generates new images and sends them to the server.
- The **ESP32-powered picture frame(s)** follow a sleep schedule, staying off for 24 hours and waking up at 4 am. When it wakes up, it requests a picture, displays it, and then goes back to sleep.
- The **Raspberry Pi-powered picture frame(s)** host an API for displaying images, so you can send live notifications or images directly to the frame.
