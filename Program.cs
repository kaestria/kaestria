using System;
using Nexus.Machine;
using Nexus.Terminal;
using Nexus.Users;
using Nexus.FileSystem;
using Nexus.Utils;
using Nexus.API;

class Program
{
    static void Main(string[] args)
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        
        MachineManager machineManager = new MachineManager();
        string selectedMachine = machineManager.SelectBoot();
        
        string machinePath = machineManager.GetMachinePath(selectedMachine);
        NexusFS.SetRoot(machinePath);
        UserManager.Init(machinePath);
        
        Neofetch.Display(selectedMachine);
        
        Console.WriteLine("[Nexus ready. Type 'help' for available commands.]");
        Console.WriteLine();
        
        var api = new NexusAPI(machinePath, selectedMachine);
        api.Start();
        
        TerminalBase terminal = new TerminalBase(selectedMachine);
        terminal.Run();
        
        api.Stop();
    }
}
