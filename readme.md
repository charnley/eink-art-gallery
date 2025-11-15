
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

    subgraph "Display Workflow"
        I[Frame wakes up] --> J[Request Image]
        J --> K[Get Frame's Group]
        K --> L[Select Active Prompt]
        L --> M[Get Random Image]
        M --> N[Display Image]
        N --> O[Record Battery State]
    end

    subgraph "Scheduled Operations"
        P[Cron: Prompt Rotation] --> Q[Rotate Group Prompts]
        R[Cron: Frame Update] --> S[Push to PUSH Frames]
    end

    D --> H
    H --> L
    Q --> H
    S --> N

    classDef db fill:#e1f5fe
    classDef process fill:#f3e5f5
    classDef schedule fill:#fff3e0

    class A,B,C,D,E,F,G,H process
    class I,J,K,L,M,N,O db
    class P,Q,R,S schedule
```

- The **picture server** stores a list of AI prompts, each with its associated images, in an SQLite database. For our setup, this is hosted on **Home Assistant as an Add-on**, but it could easily run on any Docker hosting service.
- Every night, the **desktop computer** checks the picture server for prompts that need images. For each prompt, the desktop computer generates new images and sends them to the server.
- The **ESP32-powered picture frame(s)** follow a sleep schedule, staying off for 24 hours and waking up at 4 am. When it wakes up, it requests a picture, displays it, and then goes back to sleep.
- The **Raspberry Pi-powered picture frame(s)** host an API for displaying images, so you can send live notifications or images directly to the frame.
