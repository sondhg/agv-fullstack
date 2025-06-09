```mermaid
flowchart LR
    web[Web app]
        user[User authentication]
        map[Create map layout]
        orders[Create orders]
        
        manage[Manage AGVs]
            dispatch[Dispatch orders to AGVs]
            schedule[Schedule start time]
            instructions[Send navigation instructions]
            realtime[Display real-time data]

    web--> user
    web--> map
    web--> orders
    web--> manage
        manage--> dispatch
        manage--> schedule
        manage--> instructions
        manage--> realtime

```
