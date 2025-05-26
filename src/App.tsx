import { Tab } from '@headlessui/react';
import FileUpload from './FileUpload';
import MultimodalSearch from './MultimodalSearch';

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ');
}

export default function App() {
  const tabs = ['File Upload', 'Multimodal Search'];

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="w-full max-w-4xl mx-auto">
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
                </Tab> ))}
          </Tab.List>

          <Tab.Panels className="mt-4">
            <Tab.Panel>
                <FileUpload />
            </Tab.Panel>
            <Tab.Panel>
                <MultimodalSearch />
            </Tab.Panel>
          </Tab.Panels>

        </Tab.Group>
      </div>
    </div>
  );
}
