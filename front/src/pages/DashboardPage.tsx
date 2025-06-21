import { MediguardApi } from "@/app/services";
import {
  Activity,
  AlertCircle,
  AlertTriangle,
  BarChart3,
  Bell,
  CheckCircle,
  Clock,
  Edit,
  Eye,
  FileText,
  Filter,
  Home,
  LogOut,
  Pill,
  Plus,
  Search,
  Settings,
  Trash2,
  User,
  XCircle
} from "lucide-react";
import { useEffect, useState } from "react";


interface IMockMedication {
  id: string;
  name: string;
  generic_name: string;
  strength: string;
  dosage_form: string;
  dosage_amount: number;
  dosage_unit: string;
  frequency: string;
  start_date: string;
  status: string;
  is_critical: boolean;
  quantity_remaining: number;
  total_quantity: number;
  instructions: string;
  prescribing_doctor: string;
}

const mockMedications: IMockMedication[] = [
  {
    id: "1",
    name: "Paracetamol",
    generic_name: "Acetaminophen",
    strength: "500mg",
    dosage_form: "tablet",
    dosage_amount: 1,
    dosage_unit: "tablet",
    frequency: "twice_daily",
    start_date: "2024-01-15T00:00:00Z",
    status: "active",
    is_critical: false,
    quantity_remaining: 20,
    total_quantity: 30,
    instructions: "Take with food",
    prescribing_doctor: "Dr. Smith",
  },
  {
    id: "2",
    name: "Lisinopril",
    generic_name: "Lisinopril",
    strength: "10mg",
    dosage_form: "tablet",
    dosage_amount: 1,
    dosage_unit: "tablet",
    frequency: "once_daily",
    start_date: "2024-01-10T00:00:00Z",
    status: "active",
    is_critical: true,
    quantity_remaining: 5,
    total_quantity: 30,
    instructions: "Take in the morning",
    prescribing_doctor: "Dr. Johnson",
  },
];


interface IMockReminder {
  id: string;
  medication_id: string;
  scheduled_time: string;
  status: string;
  medication: {
    name: string;
    strength: string;
  };
}
const mockReminders: IMockReminder[] = [
  {
    id: "1",
    medication_id: "1",
    scheduled_time: "2024-06-21T14:00:00Z",
    status: "pending",
    medication: { name: "Paracetamol", strength: "500mg" },
  },
  {
    id: "2",
    medication_id: "2",
    scheduled_time: "2024-06-21T08:00:00Z",
    status: "taken",
    medication: { name: "Lisinopril", strength: "10mg" },
  },
];

interface IMockLog {
  id: string;
  medication_id: string;
  scheduled_time: string;
  actual_time: string;
  status: string;
  dosage_taken: number;
  effectiveness_rating: number;
  medication: {
    name: string;
    strength: string;
  };
}
const mockLogs: IMockLog[] = [
  {
    id: "1",
    medication_id: "1",
    scheduled_time: "2024-06-21T08:00:00Z",
    actual_time: "2024-06-21T08:15:00Z",
    status: "taken",
    dosage_taken: 1,
    effectiveness_rating: 4,
    medication: { name: "Paracetamol", strength: "500mg" },
  },
  {
    id: "2",
    medication_id: "2",
    scheduled_time: "2024-06-20T08:00:00Z",
    actual_time: "2024-06-20T08:15:00Z",
    status: "missed",
    medication: { name: "Lisinopril", strength: "10mg" },
    dosage_taken: 0,
    effectiveness_rating: 0
  },
];

const MedicationDashboard = () => {
  const [activeTab, setActiveTab] = useState<string>("dashboard");
  const [medications, setMedications] = useState<IMockMedication[]>(mockMedications);
  const [reminders, ] = useState(mockReminders);
  const [logs] = useState(mockLogs);
  const [showAddMedication, setShowAddMedication] = useState(false);
  const [selectedMedication, setSelectedMedication] = useState<IMockMedication | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState("all");


  const [email, setEmail] = useState('example.com');
  const [fullName, setFullName] = useState('John Doe');
  const getUser = new MediguardApi().baseApi.getUser();

  useEffect(() => {
    getUser.then((user) => {
      console.log(user);
      if (user) {
        setFullName(user.first_name + " " + user.last_name);
        setEmail(user.email);
      }
    });
  }, []);


  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("userEmail");
    window.location.href = "/login";
  };

  // Analytics calculations
  const totalMedications = medications.length;
  const activeMedications = medications.filter(
    (m) => m.status === "active"
  ).length;
  const criticalMedications = medications.filter((m) => m.is_critical).length;
  const lowStockMedications = medications.filter(
    (m) => m.quantity_remaining && m.quantity_remaining < 10
  ).length;
  const todayReminders = reminders.filter((r) => {
    const today = new Date().toDateString();
    return new Date(r.scheduled_time).toDateString() === today;
  }).length;
  const adherenceRate =
    logs.length > 0
      ? (
          (logs.filter((l) => l.status === "taken").length / logs.length) *
          100
        ).toFixed(1)
      : 0;

  const MedicationForm = ({ medication, onSave, onCancel }: {
    medication?: IMockMedication;
    onSave: (medication: IMockMedication) => void;
    onCancel: () => void;
  }) => {
    const [formData, setFormData] = useState(
      medication || {
        name: "",
        generic_name: "",
        strength: "",
        dosage_form: "tablet",
        dosage_amount: 1,
        dosage_unit: "tablet",
        frequency: "once_daily",
        start_date: new Date().toISOString().split("T")[0],
        status: "active",
        is_critical: false,
        instructions: "",
        prescribing_doctor: "",
        total_quantity: 30,
        quantity_remaining: 30,
      }
    );

    const handleSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      onSave(formData as IMockMedication);
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
          <h3 className="text-xl font-bold mb-4">
            {medication ? "Edit Medication" : "Add New Medication"}
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">
                  Medication Name *
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">
                  Generic Name
                </label>
                <input
                  type="text"
                  value={formData.generic_name}
                  onChange={(e) =>
                    setFormData({ ...formData, generic_name: e.target.value })
                  }
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">
                  Strength *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g., 500mg"
                  value={formData.strength}
                  onChange={(e) =>
                    setFormData({ ...formData, strength: e.target.value })
                  }
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Form</label>
                <select
                  value={formData.dosage_form}
                  onChange={(e) =>
                    setFormData({ ...formData, dosage_form: e.target.value })
                  }
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="tablet">Tablet</option>
                  <option value="capsule">Capsule</option>
                  <option value="liquid">Liquid</option>
                  <option value="injection">Injection</option>
                  <option value="cream">Cream</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">
                  Dosage Amount
                </label>
                <input
                  type="number"
                  step="0.5"
                  value={formData.dosage_amount}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      dosage_amount: parseFloat(e.target.value),
                    })
                  }
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">
                  Frequency
                </label>
                <select
                  value={formData.frequency}
                  onChange={(e) =>
                    setFormData({ ...formData, frequency: e.target.value })
                  }
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="once_daily">Once Daily</option>
                  <option value="twice_daily">Twice Daily</option>
                  <option value="three_times_daily">Three Times Daily</option>
                  <option value="four_times_daily">Four Times Daily</option>
                  <option value="every_other_day">Every Other Day</option>
                  <option value="weekly">Weekly</option>
                  <option value="as_needed">As Needed</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">
                  Prescribing Doctor
                </label>
                <input
                  type="text"
                  value={formData.prescribing_doctor}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      prescribing_doctor: e.target.value,
                    })
                  }
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">
                  Start Date
                </label>
                <input
                  type="date"
                  value={formData.start_date}
                  onChange={(e) =>
                    setFormData({ ...formData, start_date: e.target.value })
                  }
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">
                  Total Quantity
                </label>
                <input
                  type="number"
                  value={formData.total_quantity}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      total_quantity: parseInt(e.target.value),
                    })
                  }
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">
                  Remaining Quantity
                </label>
                <input
                  type="number"
                  value={formData.quantity_remaining}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      quantity_remaining: parseInt(e.target.value),
                    })
                  }
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">
                Instructions
              </label>
              <textarea
                value={formData.instructions}
                onChange={(e) =>
                  setFormData({ ...formData, instructions: e.target.value })
                }
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                rows={3}
              />
            </div>
            <div className="flex items-center space-x-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.is_critical}
                  onChange={(e) =>
                    setFormData({ ...formData, is_critical: e.target.checked })
                  }
                  className="mr-2"
                />
                Critical Medication
              </label>
            </div>
            <div className="flex justify-end space-x-2 pt-4">
              <button
                type="button"
                onClick={onCancel}
                className="px-4 py-2 text-gray-600 bg-gray-200 rounded-lg hover:bg-gray-300"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700"
              >
                {medication ? "Update" : "Add"} Medication
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  const DashboardView = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">
                Total Medications
              </p>
              <p className="text-2xl font-bold text-gray-900">
                {totalMedications}
              </p>
            </div>
            <Pill className="h-8 w-8 text-blue-600" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">
                Active Medications
              </p>
              <p className="text-2xl font-bold text-green-600">
                {activeMedications}
              </p>
            </div>
            <Activity className="h-8 w-8 text-green-600" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">
                Today's Reminders
              </p>
              <p className="text-2xl font-bold text-orange-600">
                {todayReminders}
              </p>
            </div>
            <Bell className="h-8 w-8 text-orange-600" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">
                Adherence Rate
              </p>
              <p className="text-2xl font-bold text-purple-600">
                {adherenceRate}%
              </p>
            </div>
            <BarChart3 className="h-8 w-8 text-purple-600" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Critical Medications</h3>
          <div className="space-y-3">
            {medications
              .filter((m) => m.is_critical)
              .map((med) => (
                <div
                  key={med.id}
                  className="flex items-center justify-between p-3 bg-red-50 rounded-lg"
                >
                  <div>
                    <p className="font-medium">{med.name}</p>
                    <p className="text-sm text-gray-600">{med.strength}</p>
                  </div>
                  <AlertTriangle className="h-5 w-5 text-red-600" />
                </div>
              ))}
            {criticalMedications === 0 && (
              <p className="text-gray-500 text-center py-4">
                No critical medications
              </p>
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Low Stock Alerts</h3>
          <div className="space-y-3">
            {medications
              .filter((m) => m.quantity_remaining && m.quantity_remaining < 10)
              .map((med) => (
                <div
                  key={med.id}
                  className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg"
                >
                  <div>
                    <p className="font-medium">{med.name}</p>
                    <p className="text-sm text-gray-600">
                      {med.quantity_remaining} remaining
                    </p>
                  </div>
                  <AlertCircle className="h-5 w-5 text-yellow-600" />
                </div>
              ))}
            {lowStockMedications === 0 && (
              <p className="text-gray-500 text-center py-4">
                All medications well stocked
              </p>
            )}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Today's Schedule</h3>
        <div className="space-y-3">
          {reminders
            .filter((r) => {
              const today = new Date().toDateString();
              return new Date(r.scheduled_time).toDateString() === today;
            })
            .map((reminder) => (
              <div
                key={reminder.id}
                className="flex items-center justify-between p-3 border rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <Clock className="h-5 w-5 text-blue-600" />
                  <div>
                    <p className="font-medium">{reminder.medication.name}</p>
                    <p className="text-sm text-gray-600">
                      {new Date(reminder.scheduled_time).toLocaleTimeString(
                        [],
                        { hour: "2-digit", minute: "2-digit" }
                      )}
                    </p>
                  </div>
                </div>
                <span
                  className={`px-2 py-1 rounded-full text-xs ${
                    reminder.status === "taken"
                      ? "bg-green-100 text-green-800"
                      : reminder.status === "pending"
                      ? "bg-yellow-100 text-yellow-800"
                      : "bg-red-100 text-red-800"
                  }`}
                >
                  {reminder.status}
                </span>
              </div>
            ))}
          {todayReminders === 0 && (
            <p className="text-gray-500 text-center py-4">
              No reminders for today
            </p>
          )}
        </div>
      </div>
    </div>
  );

  const MedicationsView = () => {
    const filteredMedications = medications.filter((med) => {
      const matchesSearch =
        med.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        med.generic_name?.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesFilter =
        filterStatus === "all" || med.status === filterStatus;
      return matchesSearch && matchesFilter;
    });

    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">Medications</h2>
          <button
            onClick={() => setShowAddMedication(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>Add Medication</span>
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex flex-col md:flex-row gap-4 mb-6">
            <div className="flex-1">
              <div className="relative">
                <Search className="h-5 w-5 absolute left-3 top-3 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search medications..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Filter className="h-5 w-5 text-gray-400" />
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="paused">Paused</option>
                <option value="completed">Completed</option>
                <option value="discontinued">Discontinued</option>
              </select>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full table-auto">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4">Medication</th>
                  <th className="text-left py-3 px-4">Dosage</th>
                  <th className="text-left py-3 px-4">Frequency</th>
                  <th className="text-left py-3 px-4">Stock</th>
                  <th className="text-left py-3 px-4">Status</th>
                  <th className="text-left py-3 px-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredMedications.map((med) => (
                  <tr key={med.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <div>
                        <p className="font-medium">{med.name}</p>
                        <p className="text-sm text-gray-600">
                          {med.generic_name}
                        </p>
                        {med.is_critical && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-red-100 text-red-800 mt-1">
                            <AlertTriangle className="h-3 w-3 mr-1" />
                            Critical
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      {med.dosage_amount} {med.dosage_unit} ({med.strength})
                    </td>
                    <td className="py-3 px-4">
                      {med.frequency.replace("_", " ")}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-1 rounded-full text-xs ${
                          med.quantity_remaining < 10
                            ? "bg-red-100 text-red-800"
                            : med.quantity_remaining < 20
                            ? "bg-yellow-100 text-yellow-800"
                            : "bg-green-100 text-green-800"
                        }`}
                      >
                        {med.quantity_remaining}/{med.total_quantity}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-1 rounded-full text-xs ${
                          med.status === "active"
                            ? "bg-green-100 text-green-800"
                            : med.status === "paused"
                            ? "bg-yellow-100 text-yellow-800"
                            : "bg-gray-100 text-gray-800"
                        }`}
                      >
                        {med.status}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex space-x-2">
                        <button className="text-blue-600 hover:text-blue-800">
                          <Eye className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => {
                            setSelectedMedication(med as IMockMedication);
                            setShowAddMedication(true);
                          }}
                          className="text-green-600 hover:text-green-800"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        <button className="text-red-600 hover:text-red-800">
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  };

  const RemindersView = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Medication Reminders</h2>

      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="space-y-4">
          {reminders.map((reminder) => (
            <div
              key={reminder.id}
              className="flex items-center justify-between p-4 border rounded-lg"
            >
              <div className="flex items-center space-x-4">
                <div
                  className={`p-2 rounded-full ${
                    reminder.status === "taken"
                      ? "bg-green-100"
                      : reminder.status === "pending"
                      ? "bg-yellow-100"
                      : "bg-red-100"
                  }`}
                >
                  {reminder.status === "taken" ? (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  ) : reminder.status === "pending" ? (
                    <Clock className="h-5 w-5 text-yellow-600" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-600" />
                  )}
                </div>
                <div>
                  <p className="font-medium">
                    {reminder.medication.name} {reminder.medication.strength}
                  </p>
                  <p className="text-sm text-gray-600">
                    {new Date(reminder.scheduled_time).toLocaleString()}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span
                  className={`px-3 py-1 rounded-full text-xs ${
                    reminder.status === "taken"
                      ? "bg-green-100 text-green-800"
                      : reminder.status === "pending"
                      ? "bg-yellow-100 text-yellow-800"
                      : "bg-red-100 text-red-800"
                  }`}
                >
                  {reminder.status}
                </span>
                {reminder.status === "pending" && (
                  <button className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700">
                    Mark Taken
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const LogsView = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Medication Logs</h2>

      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="overflow-x-auto">
          <table className="w-full table-auto">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3 px-4">Medication</th>
                <th className="text-left py-3 px-4">Scheduled Time</th>
                <th className="text-left py-3 px-4">Actual Time</th>
                <th className="text-left py-3 px-4">Status</th>
                <th className="text-left py-3 px-4">Effectiveness</th>
                <th className="text-left py-3 px-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id} className="border-b hover:bg-gray-50">
                  <td className="py-3 px-4">
                    <p className="font-medium">{log.medication.name}</p>
                    <p className="text-sm text-gray-600">
                      {log.medication.strength}
                    </p>
                  </td>
                  <td className="py-3 px-4">
                    {new Date(log.scheduled_time).toLocaleString()}
                  </td>
                  <td className="py-3 px-4">
                    {log.actual_time
                      ? new Date(log.actual_time).toLocaleString()
                      : "-"}
                  </td>
                  <td className="py-3 px-4">
                    <span
                      className={`px-2 py-1 rounded-full text-xs ${
                        log.status === "taken"
                          ? "bg-green-100 text-green-800"
                          : log.status === "missed"
                          ? "bg-red-100 text-red-800"
                          : "bg-yellow-100 text-yellow-800"
                      }`}
                    >
                      {log.status}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    {log.effectiveness_rating ? (
                      <div className="flex items-center">
                        <span className="text-sm">
                          {log.effectiveness_rating}/5
                        </span>
                        <div className="flex ml-2">
                          {[...Array(5)].map((_, i) => (
                            <div
                              key={i}
                              className={`w-2 h-2 rounded-full mr-1 ${
                                i < log.effectiveness_rating
                                  ? "bg-yellow-400"
                                  : "bg-gray-200"
                              }`}
                            />
                          ))}
                        </div>
                      </div>
                    ) : (
                      "-"
                    )}
                  </td>
                  <td className="py-3 px-4">
                    <button className="text-blue-600 hover:text-blue-800">
                      <Eye className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const AnalyticsView = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Analytics & Reports</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">
                Total Doses Taken
              </p>
              <p className="text-2xl font-bold text-green-600">
                {logs.filter((l) => l.status === "taken").length}
              </p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-600" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Missed Doses</p>
              <p className="text-2xl font-bold text-red-600">
                {logs.filter((l) => l.status === "missed").length}
              </p>
            </div>
            <XCircle className="h-8 w-8 text-red-600" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">
                Adherence Rate
              </p>
              <p className="text-2xl font-bold text-blue-600">
                {adherenceRate}%
              </p>
            </div>
            <BarChart3 className="h-8 w-8 text-blue-600" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">
                Avg Effectiveness
              </p>
              <p className="text-2xl font-bold text-purple-600">
                {logs.filter((l) => l.effectiveness_rating).length > 0
                  ? (
                      logs
                        .filter((l) => l.effectiveness_rating)
                        .reduce((sum, l) => sum + l.effectiveness_rating, 0) /
                      logs.filter((l) => l.effectiveness_rating).length
                    ).toFixed(1)
                  : "0"}
              </p>
            </div>
            <Activity className="h-8 w-8 text-purple-600" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Weekly Adherence Trend</h3>
          <div className="space-y-3">
            {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map(
              (day, index) => {
                const dayLogs = logs.filter(
                  (l) => new Date(l.scheduled_time).getDay() === (index + 1) % 7
                );
                const adherence =
                  dayLogs.length > 0
                    ? (dayLogs.filter((l) => l.status === "taken").length /
                        dayLogs.length) *
                      100
                    : 0;
                return (
                  <div key={day} className="flex items-center justify-between">
                    <span className="text-sm font-medium w-12">{day}</span>
                    <div className="flex-1 mx-4 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${adherence}%` }}
                      ></div>
                    </div>
                    <span className="text-sm text-gray-600 w-12 text-right">
                      {adherence.toFixed(0)}%
                    </span>
                  </div>
                );
              }
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold mb-4">
            Medication Effectiveness
          </h3>
          <div className="space-y-3">
            {medications.map((med) => {
              const medLogs = logs.filter(
                (l) => l.medication_id === med.id && l.effectiveness_rating
              );
              const avgRating =
                medLogs.length > 0
                  ? medLogs.reduce(
                      (sum, l) => sum + l.effectiveness_rating,
                      0
                    ) / medLogs.length
                  : 0;
              return (
                <div key={med.id} className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="font-medium">{med.name}</p>
                    <div className="flex items-center mt-1">
                      {[...Array(5)].map((_, i) => (
                        <div
                          key={i}
                          className={`w-3 h-3 rounded-full mr-1 ${
                            i < Math.round(avgRating)
                              ? "bg-yellow-400"
                              : "bg-gray-200"
                          }`}
                        />
                      ))}
                      <span className="ml-2 text-sm text-gray-600">
                        {avgRating.toFixed(1)}/5 ({medLogs.length} reviews)
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Recent Activity Summary</h3>
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <p className="text-2xl font-bold text-green-600">
                {
                  logs.filter((l) => {
                    const weekAgo = new Date();
                    weekAgo.setDate(weekAgo.getDate() - 7);
                    return (
                      new Date(l.scheduled_time) >= weekAgo &&
                      l.status === "taken"
                    );
                  }).length
                }
              </p>
              <p className="text-sm text-gray-600">Doses taken this week</p>
            </div>
            <div className="text-center p-4 bg-red-50 rounded-lg">
              <p className="text-2xl font-bold text-red-600">
                {
                  logs.filter((l) => {
                    const weekAgo = new Date();
                    weekAgo.setDate(weekAgo.getDate() - 7);
                    return (
                      new Date(l.scheduled_time) >= weekAgo &&
                      l.status === "missed"
                    );
                  }).length
                }
              </p>
              <p className="text-sm text-gray-600">Doses missed this week</p>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <p className="text-2xl font-bold text-blue-600">
                {Math.round(
                  (logs.filter((l) => {
                    const weekAgo = new Date();
                    weekAgo.setDate(weekAgo.getDate() - 7);
                    return (
                      new Date(l.scheduled_time) >= weekAgo &&
                      l.status === "taken"
                    );
                  }).length /
                    Math.max(
                      logs.filter((l) => {
                        const weekAgo = new Date();
                        weekAgo.setDate(weekAgo.getDate() - 7);
                        return new Date(l.scheduled_time) >= weekAgo;
                      }).length,
                      1
                    )) *
                    100
                )}
                %
              </p>
              <p className="text-sm text-gray-600">Weekly adherence</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const SettingsView = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Settings</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Notification Settings</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Medication Reminders</p>
                <p className="text-sm text-gray-600">
                  Get notified when it's time to take medication
                </p>
              </div>
              <input type="checkbox" defaultChecked className="toggle" />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Refill Reminders</p>
                <p className="text-sm text-gray-600">
                  Get notified when medication is running low
                </p>
              </div>
              <input type="checkbox" defaultChecked className="toggle" />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Missed Dose Alerts</p>
                <p className="text-sm text-gray-600">
                  Get alerted when you miss a dose
                </p>
              </div>
              <input type="checkbox" defaultChecked className="toggle" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Profile Settings</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Email</label>
              <input
                type="email"
                value={email}
                readOnly
                className="w-full px-3 py-2 border rounded-lg bg-gray-50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Full Name</label>
              <input
                type="text"
                value={fullName}
                readOnly
                className="w-full px-3 py-2 border rounded-lg bg-gray-50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">
                Time Zone
              </label>
              <select className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500">
                <option>UTC-5 (Eastern Time)</option>
                <option>UTC-6 (Central Time)</option>
                <option>UTC-7 (Mountain Time)</option>
                <option>UTC-8 (Pacific Time)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">
                Default Snooze Duration
              </label>
              <select className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500">
                <option>5 minutes</option>
                <option>10 minutes</option>
                <option>15 minutes</option>
                <option>30 minutes</option>
              </select>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Data & Privacy</h3>
          <div className="space-y-4">
            <button className="w-full text-left p-3 border rounded-lg hover:bg-gray-50">
              <p className="font-medium">Export My Data</p>
              <p className="text-sm text-gray-600">
                Download all your medication data
              </p>
            </button>
            <button className="w-full text-left p-3 border rounded-lg hover:bg-gray-50">
              <p className="font-medium">Privacy Settings</p>
              <p className="text-sm text-gray-600">
                Manage your privacy preferences
              </p>
            </button>
            <button className="w-full text-left p-3 border border-red-200 rounded-lg hover:bg-red-50 text-red-600">
              <p className="font-medium">Delete Account</p>
              <p className="text-sm">
                Permanently delete your account and data
              </p>
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Emergency Contacts</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                Primary Contact
              </label>
              <input
                type="text"
                placeholder="Contact name"
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 mb-2"
              />
              <input
                type="tel"
                placeholder="Phone number"
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">
                Doctor/Pharmacy
              </label>
              <input
                type="text"
                placeholder="Doctor/Pharmacy name"
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 mb-2"
              />
              <input
                type="tel"
                placeholder="Phone number"
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const handleSaveMedication = (medicationData: IMockMedication) => {
    if (selectedMedication) {
      // Update existing medication
      setMedications((prev) =>
        prev.map((med) =>
          med.id === selectedMedication.id
            ? { ...medicationData, id: selectedMedication.id }
            : med
        )
      );
    } else {
      // Add new medication
      const newMedication = {
        ...medicationData,
        id: Date.now().toString(),
      };
      setMedications((prev) => [...prev, newMedication]);
    }
    setShowAddMedication(false);
    setSelectedMedication(null);
  };

  const sidebarItems = [
    { id: "dashboard", label: "Dashboard", icon: Home },
    { id: "medications", label: "Medications", icon: Pill },
    { id: "reminders", label: "Reminders", icon: Bell },
    { id: "logs", label: "Medication Logs", icon: FileText },
    { id: "analytics", label: "Analytics", icon: BarChart3 },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-gray-100 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-lg">
        <div className="p-4 border-b">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Pill className="h-5 w-5 text-white" />
            </div>
            <h1 className="text-xl font-bold text-gray-800">RemediCall</h1>
          </div>
        </div>

        <nav className="mt-6">
          {sidebarItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center space-x-3 px-4 py-3 text-left hover:bg-blue-50 transition-colors ${
                activeTab === item.id
                  ? "bg-blue-50 border-r-2 border-blue-600 text-blue-600"
                  : "text-gray-600"
              }`}
            >
              <item.icon className="h-5 w-5" />
              <span>{item.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white shadow-sm border-b px-6 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold text-gray-800 capitalize">
                {activeTab === "dashboard" ? "Dashboard" : activeTab}
              </h2>
              <p className="text-gray-600 text-sm mt-1">
                {new Date().toLocaleDateString("en-US", {
                  weekday: "long",
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <User className="h-5 w-5 text-gray-400" />
                <span className="text-sm text-gray-600">{email}</span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              >
                <LogOut className="h-4 w-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 p-6 overflow-y-auto">
          {activeTab === "dashboard" && <DashboardView />}
          {activeTab === "medications" && <MedicationsView />}
          {activeTab === "reminders" && <RemindersView />}
          {activeTab === "logs" && <LogsView />}
          {activeTab === "analytics" && <AnalyticsView />}
          {activeTab === "settings" && <SettingsView />}
        </main>
      </div>

      {/* Medication Form Modal */}
      {showAddMedication && (
        <MedicationForm
          medication={selectedMedication || undefined}
          onSave={handleSaveMedication}
          onCancel={() => {
            setShowAddMedication(false);
            setSelectedMedication(null);
          }}
        />
      )}
    </div>
  );
};

export default MedicationDashboard;
