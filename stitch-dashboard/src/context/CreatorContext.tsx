import React, { createContext, useContext, useState, ReactNode } from 'react';

// Hardcoded list of creators available in our Mock Data
export const AVAILABLE_CREATORS = [
    { id: 'UCX6OQ3DkcsbYNE6H8uQQuVA', name: 'MrBeast', platform: 'YouTube' },
    { id: 'UCzJo1FjvvTYrQl2m7hrxOyw', name: 'IShowSpeed', platform: 'YouTube' },
    { id: 'UCq-Fj5jknLsUf-MWSy4_brA', name: 'T-Series', platform: 'YouTube' },
    { id: 'UCbCmjCuTUZos6Inko4u57UQ', name: 'Cocomelon', platform: 'YouTube' },
    { id: 'UC-lHJZR3Gqxm24_Vd_AJ5Yw', name: 'PewDiePie', platform: 'YouTube' },
    { id: 'UC7_YxT-KID8kRbqZo7MyscQ', name: 'Markiplier', platform: 'YouTube' },
    { id: 'UCBJycsmduvYEL83R_U4JriQ', name: 'MKBHD', platform: 'YouTube' },
    { id: 'UCRijo3ddMTht_IHyNSNXpNQ', name: 'Dude Perfect', platform: 'YouTube' },
    { id: 'UCHnyfMqiRRG1u-2MsSQLbXA', name: 'Veritasium', platform: 'YouTube' },
    { id: 'UC78cxCAcp7JfQPgKxYdyGrg', name: 'Emma Chamberlain', platform: 'YouTube' },
    // Instagram Creators (using IDs from real_world_creators.py)
    { id: '173560420', name: 'Cristiano Ronaldo', platform: 'Instagram' },
    { id: 'kyliejenner', name: 'Kylie Jenner', platform: 'Instagram' }, // Using username as ID for some if ID missed
    { id: 'leomessi', name: 'Lionel Messi', platform: 'Instagram' },
    { id: 'charlidamelio', name: 'Charli D\'Amelio', platform: 'Instagram' },
    { id: 'zachking', name: 'Zach King', platform: 'Instagram' }
];

interface CreatorContextType {
    selectedCreatorId: string;
    setSelectedCreatorId: (id: string) => void;
    availableCreators: typeof AVAILABLE_CREATORS;
    selectedCreator: typeof AVAILABLE_CREATORS[0] | undefined;
}

const CreatorContext = createContext<CreatorContextType | undefined>(undefined);

export const CreatorProvider = ({ children }: { children: ReactNode }) => {
    // Default to MrBeast
    const [selectedCreatorId, setSelectedCreatorId] = useState<string>('UCX6OQ3DkcsbYNE6H8uQQuVA');

    const selectedCreator = AVAILABLE_CREATORS.find(c => c.id === selectedCreatorId);

    return (
        <CreatorContext.Provider value={{ selectedCreatorId, setSelectedCreatorId, availableCreators: AVAILABLE_CREATORS, selectedCreator }}>
            {children}
        </CreatorContext.Provider>
    );
};

export const useCreator = () => {
    const context = useContext(CreatorContext);
    if (context === undefined) {
        throw new Error('useCreator must be used within a CreatorProvider');
    }
    return context;
};
