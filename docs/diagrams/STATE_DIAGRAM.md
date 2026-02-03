# State Diagram

Diagram state untuk berbagai komponen dalam PONG-CLI.

## Application States

```mermaid
stateDiagram-v2
    [*] --> Initializing
    
    Initializing --> Menu: Components Ready
    
    state Menu {
        [*] --> MainMenu
        MainMenu --> HostSelected: Select Host
        MainMenu --> JoinSelected: Select Join
        MainMenu --> AISelected: Select VS AI
        MainMenu --> [*]: Quit
        
        AISelected --> DifficultyMenu
        DifficultyMenu --> EasySelected
        DifficultyMenu --> MediumSelected
        DifficultyMenu --> HardSelected
    }
    
    Menu --> HostLobby: Host Game
    Menu --> JoinConnect: Join Game
    Menu --> VSAIGame: VS AI
    Menu --> [*]: Quit
    
    state HostLobby {
        [*] --> WaitingPlayer
        WaitingPlayer --> PlayerConnected: Client Joins
        PlayerConnected --> GameReady
        GameReady --> [*]: TAB Pressed
    }
    
    state JoinConnect {
        [*] --> EnterIP
        EnterIP --> EnterPort
        EnterPort --> Connecting
        Connecting --> Connected: Success
        Connecting --> Failed: Error
        Failed --> [*]
    }
    
    JoinConnect --> ClientLobby: Connected
    
    state ClientLobby {
        [*] --> WaitingHost
        WaitingHost --> [*]: Host Starts
    }
    
    HostLobby --> MultiplayerGame: Start
    ClientLobby --> MultiplayerGame: Host Starts
    
    state MultiplayerGame {
        [*] --> Playing
        Playing --> GoalScored: Ball Out
        GoalScored --> Playing: Reset Ball
        Playing --> [*]: Win Condition
    }
    
    state VSAIGame {
        [*] --> AIPlaying
        AIPlaying --> AIGoalScored: Ball Out
        AIGoalScored --> AIPlaying: Reset Ball
        AIPlaying --> [*]: Win Condition
    }
    
    MultiplayerGame --> GameOver
    VSAIGame --> GameOver
    
    GameOver --> Menu: Timeout/Return
```

## Power-up States

```mermaid
stateDiagram-v2
    [*] --> Inactive
    
    Inactive --> Spawning: Spawn Timer
    
    state Spawning {
        [*] --> SelectType
        SelectType --> SelectPosition
        SelectPosition --> [*]
    }
    
    Spawning --> OnField: Spawn Complete
    
    state OnField {
        [*] --> Visible
        Visible --> [*]: Ball Collision
    }
    
    OnField --> Collected: Ball Touches
    
    state Collected {
        [*] --> ApplyEffect
        ApplyEffect --> EffectActive
        EffectActive --> EffectExpired: 5 seconds
    }
    
    Collected --> EffectActive: Applied
    EffectActive --> [*]: Remove Effect
```

## Ball States

```mermaid
stateDiagram-v2
    [*] --> Center
    
    Center --> MovingRight: Game Start (random)
    Center --> MovingLeft: Game Start (random)
    
    state MovingRight {
        [*] --> Traveling
        Traveling --> NearGoal: x > WIDTH-8
        NearGoal --> PaddleZone: x > WIDTH-5
    }
    
    state MovingLeft {
        [*] --> Traveling
        Traveling --> NearGoal: x < 8
        NearGoal --> PaddleZone: x < 5
    }
    
    MovingRight --> WallBounce: y <= 0 or y >= HEIGHT
    MovingLeft --> WallBounce: y <= 0 or y >= HEIGHT
    WallBounce --> MovingRight: vy reversed
    WallBounce --> MovingLeft: vy reversed
    
    MovingRight --> PaddleHit: Hit Right Paddle
    MovingLeft --> PaddleHit: Hit Left Paddle
    
    PaddleHit --> MovingLeft: From Right
    PaddleHit --> MovingRight: From Left
    
    MovingRight --> Goal: x >= WIDTH
    MovingLeft --> Goal: x <= 0
    
    Goal --> Center: Reset
```

## AI Controller States

```mermaid
stateDiagram-v2
    [*] --> Idle
    
    Idle --> Tracking: Game Active
    
    state Tracking {
        [*] --> Observing
        Observing --> Predicting: Ball Moving Toward
        Predicting --> Calculating: Prediction Made
        Calculating --> Moving: Target Set
        Moving --> Waiting: Move Executed
        Waiting --> Observing: Reaction Time Passed
    }
    
    state "Difficulty Modifiers" as DM {
        Easy: reaction=0.3s, accuracy=0.5
        Medium: reaction=0.15s, accuracy=0.7
        Hard: reaction=0.05s, accuracy=0.9
    }
    
    Tracking --> Idle: Game Over
```

## Input Handler States

```mermaid
stateDiagram-v2
    [*] --> Stopped
    
    Stopped --> Starting: start()
    
    state Starting {
        [*] --> CreateThread
        CreateThread --> SetRawMode
        SetRawMode --> [*]
    }
    
    Starting --> Running: Thread Started
    
    state Running {
        [*] --> WaitingInput
        
        state WaitingInput {
            [*] --> CheckStdin
            CheckStdin --> KeyAvailable: Key Pressed
            CheckStdin --> NoKey: Timeout
            NoKey --> CheckStdin: Sleep 10ms
        }
        
        KeyAvailable --> ProcessKey
        
        state ProcessKey {
            [*] --> CheckEscape
            CheckEscape --> ArrowKey: Escape Sequence
            CheckEscape --> NormalKey: Regular Char
            ArrowKey --> StoreKey
            NormalKey --> StoreKey
        }
        
        ProcessKey --> WaitingInput: Key Stored
    }
    
    Running --> Stopping: stop()
    
    state Stopping {
        [*] --> SetFlag
        SetFlag --> RestoreTerminal
        RestoreTerminal --> JoinThread
    }
    
    Stopping --> Stopped: Thread Joined
```

## Effect Animation States

```mermaid
stateDiagram-v2
    [*] --> Inactive
    
    Inactive --> Starting: Trigger Effect
    
    state "Goal Explosion" as GE {
        [*] --> Frame1
        Frame1 --> Frame2: 100ms
        Frame2 --> Frame3: 100ms
        Frame3 --> Frame4: 100ms
        Frame4 --> Frame5: 100ms
        Frame5 --> [*]: Complete
    }
    
    state "Ball Trail" as BT {
        [*] --> Position1
        Position1 --> Position2: Ball Moves
        Position2 --> Position3: Ball Moves
        Position3 --> Position4: Ball Moves
        Position4 --> Position5: Ball Moves
        Position5 --> Position1: Oldest Removed
    }
    
    state "Paddle Hit" as PH {
        [*] --> Flash1
        Flash1 --> Flash2: 50ms
        Flash2 --> Flash3: 50ms
        Flash3 --> Flash4: 50ms
        Flash4 --> [*]: Complete
    }
    
    Starting --> GE: Goal
    Starting --> BT: Ball Move
    Starting --> PH: Paddle Hit
    
    GE --> Inactive: Finished
    PH --> Inactive: Finished
```
