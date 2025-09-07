import { configureStore } from '@reduxjs/toolkit';
import advancedModeReducer from '@/features/advanced-mode/advancedModeSlice';

// TODO: Use RTK Query to fetch data from redis per chat

export const store = configureStore({
    reducer: {
        advancedMode: advancedModeReducer,
    },
});

export type AppStore = typeof store;
export type RootState = ReturnType<AppStore['getState']>;
export type AppDispatch = AppStore['dispatch'];