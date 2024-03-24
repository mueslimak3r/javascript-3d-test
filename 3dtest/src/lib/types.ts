type Day = {
	count: number
	day: number
	level: number
	month: string
	name: string
	year: number
}

export interface WarsState {
    current: string
    seasons: string[]
}

export interface Position {
  x: number
  y: number
}

export interface War {
    capitals: any[]
    end_date: string
    home_worlds: HomeWorld[]
    minimum_client_version: string
    planet_permanent_effects: any[]
    planets: Planet[]
    start_date: string
    war_id: number
  }
  
  export interface HomeWorld {
    planets: Planet[]
    race: string
  }
  
  export interface Planet {
    disabled: boolean
    hash: number
    index: number
    initial_owner: string
    max_health: number
    name: string
    position: Position
    sector: string
    waypoints: number[]
  }