import { create } from 'zustand'

const useCarsStore = create((set) => ({
  cars: [],
  total: 0,
  page: 1,
  pageSize: 20,
  filters: {},
  
  setCars: (cars) => set({ cars }),
  setTotal: (total) => set({ total }),
  setPage: (page) => set({ page }),
  setFilters: (filters) => set({ filters }),
  
  addCar: (car) => set((state) => ({ cars: [car, ...state.cars] })),
  removeCar: (id) => set((state) => ({ cars: state.cars.filter(car => car.id !== id) })),
  updateCar: (id, updates) => set((state) => ({
    cars: state.cars.map(car => car.id === id ? { ...car, ...updates } : car)
  })),
}))

export default useCarsStore
