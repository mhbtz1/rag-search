import { useState, useEffect } from 'react';
import { Tab } from '@headlessui/react';
import FileUpload from './FileUpload';
import MultimodalSearch from './MultimodalSearch';
import AuthForm from './AuthForm';
import ImageIngestion from './ImageIngestion'
import ChatBox from './ChatBox'

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ');
}

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) setIsAuthenticated(true);
  }, []);

  if (!isAuthenticated) {
    return <AuthForm onAuthSuccess={() => setIsAuthenticated(true)} />;
  }

  const tabs = ['File Upload', 'Multimodal Search', "Image Ingestion"];

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="w-full max-w-4xl mx-auto">
        <button
          className="absolute top-4 right-4 text-sm text-red-600 hover:underline"
          onClick={() => {
            localStorage.removeItem('authToken');
            setIsAuthenticated(false);
          }}
        >
          Logout
        </button>

        <Tab.Group>
          <Tab.List className="flex space-x-2 rounded-xl bg-gray-200 p-2 shadow mb-4">
            {tabs.map((tab) => (
              <Tab
                key={tab}
                className={({ selected }) =>
                  classNames(
                    'w-full rounded-lg py-2.5 text-sm font-medium leading-5 text-center',
                    selected
                      ? 'bg-blue-600 text-white shadow'
                      : 'text-blue-700 bg-white hover:bg-blue-100 hover:text-blue-800'
                  )
                }
              >
                {tab}
              </Tab>
            ))}
          </Tab.List>

          <Tab.Panels className="mt-4">
            <Tab.Panel>
              <FileUpload />
            </Tab.Panel>
            <Tab.Panel>
              <MultimodalSearch />
            </Tab.Panel>
            <Tab.Panel>
                <ImageIngestion/>
            </Tab.Panel>
            <Tab.Panel>
                <ChatBox/>
            </Tab.Panel>
          </Tab.Panels>
        </Tab.Group>
      </div>
    </div>
  );
}
